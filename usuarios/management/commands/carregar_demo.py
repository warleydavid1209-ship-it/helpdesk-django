"""Carrega dados de demonstração (equivalente ao sql/02_dml_dados_iniciais.sql).

Uso: python manage.py carregar_demo
Todos os usuários de demonstração usam a senha  Senha@123  (apenas para testes).
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from chamados import services
from chamados.models import Categoria, Chamado
from usuarios.models import Departamento, Usuario

SENHA = "Senha@123"


class Command(BaseCommand):
    help = "Cria departamentos, categorias, usuários e chamados de demonstração."

    @transaction.atomic
    def handle(self, *args, **opts):
        ti, infra, adm = [Departamento.objects.get_or_create(nome=n, defaults={"descricao": d})[0] for n, d in [
            ("Tecnologia da Informação", "Suporte a computadores, sistemas e rede"),
            ("Infraestrutura", "Manutenção predial, elétrica e climatização"),
            ("Administrativo", "Solicitações de documentos, compras e acessos")]]
        cats = {}
        for nome, dep in [("Hardware", ti), ("Software", ti), ("Rede e Internet", ti),
                          ("Manutenção Predial", infra), ("Climatização", infra), ("Solicitação Administrativa", adm)]:
            cats[nome] = Categoria.objects.get_or_create(nome=nome, departamento=dep)[0]

        def usuario(email, nome, perfil, dep):
            u, criado = Usuario.objects.get_or_create(email=email, defaults={"nome": nome, "perfil": perfil, "departamento": dep})
            if criado:
                u.set_password(SENHA)
                u.save()
            return u

        admin = usuario("admin@helpdesk.com", "Administrador do Sistema", "admin", ti)
        carlos = usuario("carlos@helpdesk.com", "Carlos Técnico", "tecnico", ti)
        marina = usuario("marina@helpdesk.com", "Marina Técnica", "tecnico", infra)
        ana = usuario("ana@cliente.com", "Ana Cliente", "cliente", adm)
        joao = usuario("joao@cliente.com", "João Cliente", "cliente", adm)

        if Chamado.objects.exists():
            self.stdout.write("Chamados já existem; nada a fazer.")
            return
        c1 = services.abrir_chamado(ana, "Computador não liga", "O computador da recepção não liga desde ontem à tarde.", cats["Hardware"], "alta")
        services.assumir_chamado(c1, carlos)
        services.comentar(c1, carlos, "Vou verificar a fonte de alimentação ainda hoje.")
        services.comentar(c1, carlos, "Suspeita de fonte queimada. Verificar estoque.", interno=True)
        services.abrir_chamado(joao, "Instalar pacote Office", "Preciso do pacote Office instalado na máquina nova.", cats["Software"])
        c3 = services.abrir_chamado(ana, "Wi-Fi caindo na sala 2", "A conexão cai a cada 10 minutos na sala de reuniões 2.", cats["Rede e Internet"])
        services.assumir_chamado(c3, carlos)
        services.alterar_status(c3, carlos, "aguardando")
        c4 = services.abrir_chamado(joao, "Lâmpada queimada no corredor", "Duas lâmpadas queimadas no corredor do 2º andar.", cats["Manutenção Predial"], "baixa")
        services.assumir_chamado(c4, marina)
        services.alterar_status(c4, marina, "resolvido")
        c5 = services.abrir_chamado(ana, "Ar-condicionado vazando", "O ar-condicionado da sala 5 está pingando água no chão.", cats["Climatização"], "alta")
        services.assumir_chamado(c5, marina)
        services.alterar_status(c5, marina, "fechado")
        services.abrir_chamado(joao, "Sistema fora do ar", "Ninguém consegue acessar o sistema interno.", cats["Rede e Internet"], "critica")
        self.stdout.write(self.style.SUCCESS(f"Dados de demonstração carregados. Senha dos usuários: {SENHA}"))
