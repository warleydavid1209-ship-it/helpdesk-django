import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from usuarios.models import Departamento, Usuario

from . import services
from .models import Categoria, Chamado, HistoricoStatus

MEDIA_TMP = tempfile.mkdtemp()


class BaseTeste(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.dep = Departamento.objects.create(nome="TI")
        cls.cat = Categoria.objects.create(nome="Hardware", departamento=cls.dep)
        cls.cliente = Usuario.objects.create_user("ana@x.com", "Senha@12345", nome="Ana")
        cls.outro = Usuario.objects.create_user("joao@x.com", "Senha@12345", nome="João")
        cls.tecnico = Usuario.objects.create_user("carlos@x.com", "Senha@12345", nome="Carlos", perfil="tecnico")
        cls.admin = Usuario.objects.create_superuser("admin@x.com", "Senha@12345", nome="Admin")

    def api(self, usuario=None):
        c = APIClient()
        if usuario:
            c.force_authenticate(usuario)
        return c

    def novo_chamado(self, solicitante=None, **extra):
        return services.abrir_chamado(solicitante or self.cliente, extra.get("titulo", "Computador não liga"),
                                      extra.get("descricao", "Não liga desde ontem à tarde."), self.cat)


@override_settings(MEDIA_ROOT=MEDIA_TMP)
class AutenticacaoAPITest(BaseTeste):
    def tearDown(self):
        shutil.rmtree(MEDIA_TMP, ignore_errors=True)

    def test_cadastro_cria_cliente_e_ignora_perfil_enviado(self):
        r = self.api().post("/api/auth/cadastro/", {"nome": "Maria Silva", "email": "Maria@X.com",
                                                    "senha": "Senha@12345", "perfil": "admin"}, format="json")
        self.assertEqual(r.status_code, 201)
        u = Usuario.objects.get(email="maria@x.com")
        self.assertEqual(u.perfil, "cliente")
        self.assertNotEqual(u.password, "Senha@12345")  # armazenada como hash
        self.assertNotIn("senha", r.json())

    def test_cadastro_valida_email_duplicado_e_senha_fraca(self):
        r = self.api().post("/api/auth/cadastro/", {"nome": "Ana Dois", "email": "ana@x.com", "senha": "123"}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("email", r.json())
        self.assertIn("senha", r.json())

    def test_login_ok_retorna_token(self):
        r = self.api().post("/api/auth/login/", {"email": "ana@x.com", "senha": "Senha@12345"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["token"])
        c = APIClient()
        c.credentials(HTTP_AUTHORIZATION="Token " + r.json()["token"])
        self.assertEqual(c.get("/api/auth/me/").json()["email"], "ana@x.com")

    def test_login_invalido(self):
        r = self.api().post("/api/auth/login/", {"email": "ana@x.com", "senha": "errada"}, format="json")
        self.assertEqual(r.status_code, 401)

    def test_login_usuario_inativo_e_bloqueado(self):
        Usuario.objects.filter(pk=self.cliente.pk).update(is_active=False)
        r = self.api().post("/api/auth/login/", {"email": "ana@x.com", "senha": "Senha@12345"}, format="json")
        self.assertEqual(r.status_code, 401)

    def test_endpoints_exigem_autenticacao(self):
        self.assertEqual(self.api().get("/api/chamados/").status_code, 401)
        self.assertEqual(self.api().get("/api/dashboard/").status_code, 401)

    def test_logout_invalida_token(self):
        token = self.api().post("/api/auth/login/", {"email": "ana@x.com", "senha": "Senha@12345"}, format="json").json()["token"]
        c = APIClient(); c.credentials(HTTP_AUTHORIZATION="Token " + token)
        self.assertEqual(c.post("/api/auth/logout/").status_code, 204)
        self.assertEqual(c.get("/api/auth/me/").status_code, 401)


@override_settings(MEDIA_ROOT=MEDIA_TMP)
class ChamadoAPITest(BaseTeste):
    def tearDown(self):
        shutil.rmtree(MEDIA_TMP, ignore_errors=True)

    def payload(self, **kw):
        d = {"titulo": "Impressora travada", "descricao": "A impressora não imprime nada.", "categoria": self.cat.pk}
        d.update(kw)
        return d

    def test_abrir_chamado_persiste_e_retorna(self):
        r = self.api(self.cliente).post("/api/chamados/", self.payload(prioridade="alta"), format="json")
        self.assertEqual(r.status_code, 201)
        corpo = r.json()
        self.assertEqual(corpo["status"], "aberto")
        self.assertEqual(corpo["solicitante"]["id"], self.cliente.pk)
        ch = Chamado.objects.get(pk=corpo["id"])
        self.assertEqual(ch.prioridade, "alta")
        self.assertEqual(HistoricoStatus.objects.filter(chamado=ch, status_novo="aberto").count(), 1)

    def test_abrir_chamado_valida_payload(self):
        r = self.api(self.cliente).post("/api/chamados/", {"titulo": "abc", "descricao": "curta", "categoria": 999}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(set(r.json()), {"titulo", "descricao", "categoria"})
        self.assertEqual(Chamado.objects.count(), 0)

    def test_prioridade_invalida(self):
        r = self.api(self.cliente).post("/api/chamados/", self.payload(prioridade="urgentissima"), format="json")
        self.assertEqual(r.status_code, 400)

    def test_cliente_ve_somente_os_proprios(self):
        a = self.novo_chamado(self.cliente); b = self.novo_chamado(self.outro)
        ids = [c["id"] for c in self.api(self.cliente).get("/api/chamados/").json()["results"]]
        self.assertEqual(ids, [a.pk])
        self.assertEqual(self.api(self.cliente).get(f"/api/chamados/{b.pk}/").status_code, 404)

    def test_equipe_ve_todos_e_filtra(self):
        a = self.novo_chamado(self.cliente); b = self.novo_chamado(self.outro, titulo="Wi-Fi caindo sempre")
        services.assumir_chamado(a, self.tecnico)
        c = self.api(self.tecnico)
        self.assertEqual(c.get("/api/chamados/").json()["count"], 2)
        self.assertEqual(c.get("/api/chamados/?status=em_andamento").json()["count"], 1)
        self.assertEqual(c.get("/api/chamados/?sem_tecnico=1").json()["results"][0]["id"], b.pk)
        self.assertEqual(c.get("/api/chamados/?q=wi-fi").json()["count"], 1)

    def test_assumir_muda_status_e_registra_historico(self):
        ch = self.novo_chamado()
        r = self.api(self.tecnico).post(f"/api/chamados/{ch.pk}/assumir/")
        self.assertEqual(r.status_code, 200)
        ch.refresh_from_db()
        self.assertEqual((ch.status, ch.tecnico), ("em_andamento", self.tecnico))
        self.assertEqual(ch.historico.count(), 2)

    def test_cliente_nao_assume_nem_altera_status(self):
        ch = self.novo_chamado()
        self.assertEqual(self.api(self.cliente).post(f"/api/chamados/{ch.pk}/assumir/").status_code, 403)
        self.assertEqual(self.api(self.cliente).post(f"/api/chamados/{ch.pk}/status/", {"status": "fechado"}, format="json").status_code, 403)

    def test_outro_tecnico_nao_toma_chamado_assumido(self):
        outro_t = Usuario.objects.create_user("t2@x.com", "Senha@12345", nome="T2", perfil="tecnico")
        ch = self.novo_chamado(); services.assumir_chamado(ch, self.tecnico)
        self.assertEqual(self.api(outro_t).post(f"/api/chamados/{ch.pk}/assumir/").status_code, 400)

    def test_fluxo_de_status_valido_e_fechamento(self):
        ch = self.novo_chamado(); c = self.api(self.tecnico)
        for novo in ("em_andamento", "resolvido", "fechado"):
            r = c.post(f"/api/chamados/{ch.pk}/status/", {"status": novo}, format="json")
            self.assertEqual(r.status_code, 200, r.content)
        ch.refresh_from_db()
        self.assertEqual(ch.status, "fechado"); self.assertIsNotNone(ch.fechado_em)
        self.assertEqual(ch.historico.count(), 4)

    def test_transicao_invalida_e_chamado_fechado(self):
        ch = self.novo_chamado(); c = self.api(self.tecnico)
        self.assertEqual(c.post(f"/api/chamados/{ch.pk}/status/", {"status": "resolvido"}, format="json").status_code, 400)
        services.alterar_status(ch, self.tecnico, "fechado")
        self.assertEqual(c.post(f"/api/chamados/{ch.pk}/status/", {"status": "em_andamento"}, format="json").status_code, 400)
        self.assertEqual(c.post(f"/api/chamados/{ch.pk}/status/", {"status": "inexistente"}, format="json").status_code, 400)

    def test_atribuir_somente_admin_e_somente_tecnico(self):
        ch = self.novo_chamado()
        self.assertEqual(self.api(self.tecnico).post(f"/api/chamados/{ch.pk}/atribuir/", {"tecnico_id": self.tecnico.pk}, format="json").status_code, 403)
        r = self.api(self.admin).post(f"/api/chamados/{ch.pk}/atribuir/", {"tecnico_id": self.cliente.pk}, format="json")
        self.assertEqual(r.status_code, 400)
        r = self.api(self.admin).post(f"/api/chamados/{ch.pk}/atribuir/", {"tecnico_id": self.tecnico.pk}, format="json")
        self.assertEqual(r.status_code, 200); self.assertEqual(r.json()["tecnico"]["id"], self.tecnico.pk)

    def test_prioridade_so_equipe(self):
        ch = self.novo_chamado()
        self.assertEqual(self.api(self.cliente).patch(f"/api/chamados/{ch.pk}/", {"prioridade": "critica"}, format="json").status_code, 403)
        r = self.api(self.tecnico).patch(f"/api/chamados/{ch.pk}/", {"prioridade": "critica"}, format="json")
        self.assertEqual(r.json()["prioridade"], "critica")

    def test_nota_interna_invisivel_ao_cliente(self):
        ch = self.novo_chamado()
        self.assertEqual(self.api(self.tecnico).post(f"/api/chamados/{ch.pk}/comentarios/", {"texto": "Verificar fonte", "interno": True}, format="json").status_code, 201)
        self.assertEqual(self.api(self.cliente).post(f"/api/chamados/{ch.pk}/comentarios/", {"texto": "Obrigada!"}, format="json").status_code, 201)
        vis_cliente = self.api(self.cliente).get(f"/api/chamados/{ch.pk}/comentarios/").json()
        vis_equipe = self.api(self.tecnico).get(f"/api/chamados/{ch.pk}/comentarios/").json()
        self.assertEqual(len(vis_cliente), 1); self.assertEqual(len(vis_equipe), 2)
        self.assertEqual(len(self.api(self.cliente).get(f"/api/chamados/{ch.pk}/").json()["comentarios"]), 1)

    def test_cliente_nao_cria_nota_interna(self):
        ch = self.novo_chamado()
        r = self.api(self.cliente).post(f"/api/chamados/{ch.pk}/comentarios/", {"texto": "secreto", "interno": True}, format="json")
        self.assertEqual(r.status_code, 403)

    def test_comentario_vazio_e_chamado_fechado(self):
        ch = self.novo_chamado()
        self.assertEqual(self.api(self.cliente).post(f"/api/chamados/{ch.pk}/comentarios/", {"texto": " "}, format="json").status_code, 400)
        services.alterar_status(ch, self.tecnico, "fechado")
        self.assertEqual(self.api(self.cliente).post(f"/api/chamados/{ch.pk}/comentarios/", {"texto": "ainda aí?"}, format="json").status_code, 400)

    def test_anexo_valido_e_invalido(self):
        ch = self.novo_chamado(); c = self.api(self.cliente)
        ok = c.post(f"/api/chamados/{ch.pk}/anexos/", {"arquivo": SimpleUploadedFile("foto.png", b"x" * 100)}, format="multipart")
        self.assertEqual(ok.status_code, 201)
        ruim = c.post(f"/api/chamados/{ch.pk}/anexos/", {"arquivo": SimpleUploadedFile("virus.exe", b"x")}, format="multipart")
        self.assertEqual(ruim.status_code, 400)
        grande = c.post(f"/api/chamados/{ch.pk}/anexos/", {"arquivo": SimpleUploadedFile("a.pdf", b"x" * (5 * 1024 * 1024 + 1))}, format="multipart")
        self.assertEqual(grande.status_code, 400)
        self.assertEqual(ch.anexos.count(), 1)

    def test_dashboard(self):
        self.novo_chamado(); self.novo_chamado(self.outro)
        self.assertEqual(self.api(self.cliente).get("/api/dashboard/").status_code, 403)
        d = self.api(self.tecnico).get("/api/dashboard/").json()
        self.assertEqual((d["total"], d["por_status"]["aberto"], d["sem_tecnico"]), (2, 2, 2))

    def test_listas_auxiliares(self):
        self.assertEqual(len(self.api(self.cliente).get("/api/categorias/").json()), 1)
        self.assertEqual(len(self.api(self.cliente).get("/api/departamentos/").json()), 1)
        self.assertEqual(self.api(self.cliente).get("/api/usuarios/").json()["count"], 0)  # cliente não lista usuários
        self.assertEqual(self.api(self.admin).get("/api/usuarios/?perfil=tecnico").json()["count"], 1)


@override_settings(MEDIA_ROOT=MEDIA_TMP)
class TelasTest(BaseTeste):
    def tearDown(self):
        shutil.rmtree(MEDIA_TMP, ignore_errors=True)

    def test_telas_exigem_login(self):
        for nome in ("chamado_lista", "chamado_novo", "dashboard"):
            r = self.client.get(reverse(nome))
            self.assertEqual(r.status_code, 302); self.assertIn("/login/", r["Location"])

    def test_login_pela_tela(self):
        self.assertEqual(self.client.get(reverse("login")).status_code, 200)
        r = self.client.post(reverse("login"), {"username": "ana@x.com", "password": "Senha@12345"})
        self.assertRedirects(r, reverse("chamado_lista"))
        r = self.client.post(reverse("login"), {"username": "ana@x.com", "password": "errada"})
        self.assertContains(r, "E-mail ou senha inválidos")

    def test_cadastro_pela_tela(self):
        r = self.client.post(reverse("cadastro"), {"nome": "Paulo Souza", "email": "paulo@x.com", "senha": "Senha@12345", "confirmar_senha": "Senha@12345"})
        self.assertRedirects(r, reverse("chamado_lista"))
        self.assertEqual(Usuario.objects.get(email="paulo@x.com").perfil, "cliente")
        self.client.logout()
        r = self.client.post(reverse("cadastro"), {"nome": "Xavier", "email": "y@x.com", "senha": "Senha@12345", "confirmar_senha": "outra"})
        self.assertEqual(r.status_code, 200)

    def test_abrir_chamado_pela_tela_com_anexo(self):
        self.client.force_login(self.cliente)
        self.assertEqual(self.client.get(reverse("chamado_novo")).status_code, 200)
        r = self.client.post(reverse("chamado_novo"), {"titulo": "Teclado quebrado", "categoria": self.cat.pk, "prioridade": "baixa",
                                                       "descricao": "Várias teclas não funcionam.", "arquivo": SimpleUploadedFile("t.txt", b"log")})
        ch = Chamado.objects.get(titulo="Teclado quebrado")
        self.assertRedirects(r, reverse("chamado_detalhe", args=[ch.pk]))
        self.assertEqual(ch.anexos.count(), 1)
        r = self.client.post(reverse("chamado_novo"), {"titulo": "ab", "categoria": self.cat.pk, "prioridade": "baixa", "descricao": "x"})
        self.assertEqual(r.status_code, 200); self.assertEqual(Chamado.objects.count(), 1)

    def test_detalhe_e_acoes_da_equipe(self):
        ch = self.novo_chamado()
        self.client.force_login(self.tecnico)
        self.assertContains(self.client.get(reverse("chamado_detalhe", args=[ch.pk])), "Assumir chamado")
        self.client.post(reverse("chamado_detalhe", args=[ch.pk]), {"acao": "assumir"})
        self.client.post(reverse("chamado_detalhe", args=[ch.pk]), {"acao": "status", "status": "resolvido"})
        self.client.post(reverse("chamado_detalhe", args=[ch.pk]), {"acao": "comentar", "texto": "Troquei a fonte", "interno": "on"})
        ch.refresh_from_db()
        self.assertEqual((ch.status, ch.tecnico), ("resolvido", self.tecnico))
        self.assertEqual(ch.comentarios.filter(interno=True).count(), 1)

    def test_cliente_nao_ve_chamado_alheio_nem_dashboard(self):
        ch = self.novo_chamado(self.outro)
        self.client.force_login(self.cliente)
        self.assertEqual(self.client.get(reverse("chamado_detalhe", args=[ch.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 404)

    def test_cliente_tentando_acao_de_equipe_pela_tela(self):
        ch = self.novo_chamado()
        self.client.force_login(self.cliente)
        r = self.client.post(reverse("chamado_detalhe", args=[ch.pk]), {"acao": "status", "status": "fechado"}, follow=True)
        self.assertContains(r, "Apenas técnicos e administradores")
        ch.refresh_from_db(); self.assertEqual(ch.status, "aberto")

    def test_lista_e_dashboard_da_equipe(self):
        self.novo_chamado()
        self.client.force_login(self.tecnico)
        self.assertContains(self.client.get(reverse("chamado_lista") + "?escopo=sem_tecnico"), "Computador não liga")
        self.assertContains(self.client.get(reverse("dashboard")), "Chamados no total")
