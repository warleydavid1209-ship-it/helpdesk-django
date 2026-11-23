from django.test import TestCase

from .models import Usuario


class UsuarioModelTest(TestCase):
    def test_perfis_e_permissoes_do_admin(self):
        admin = Usuario.objects.create_superuser("a@x.com", "Senha@12345", nome="A")
        cli = Usuario.objects.create_user("c@x.com", "Senha@12345", nome="C")
        self.assertTrue(admin.is_staff and admin.is_superuser and admin.eh_equipe)
        self.assertFalse(cli.is_staff or cli.eh_equipe)
        self.assertTrue(cli.check_password("Senha@12345"))

    def test_email_obrigatorio(self):
        with self.assertRaises(ValueError):
            Usuario.objects.create_user("", "x", nome="Sem email")


class CargaDemoTest(TestCase):
    def test_carregar_demo_e_idempotente(self):
        from django.core.management import call_command

        from chamados.models import Chamado

        call_command("carregar_demo", verbosity=0)
        call_command("carregar_demo", verbosity=0)
        self.assertEqual(Chamado.objects.count(), 6)
        self.assertTrue(Usuario.objects.get(email="ana@cliente.com").check_password("Senha@123"))
