from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


class Departamento(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, default="")

    class Meta:
        db_table = "departamento"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def _criar(self, email, password, **extra):
        if not email:
            raise ValueError("O e-mail é obrigatório.")
        usuario = self.model(email=self.normalize_email(email), **extra)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_user(self, email, password=None, **extra):
        extra.setdefault("perfil", Usuario.Perfil.CLIENTE)
        return self._criar(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra["perfil"] = Usuario.Perfil.ADMIN
        return self._criar(email, password, **extra)


class Usuario(AbstractBaseUser):
    """Usuário do sistema. Tabela `usuario` do MER (senha = hash do Django)."""

    class Perfil(models.TextChoices):
        CLIENTE = "cliente", "Cliente"
        TECNICO = "tecnico", "Técnico"
        ADMIN = "admin", "Administrador"

    nome = models.CharField(max_length=150)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128, db_column="senha")
    perfil = models.CharField(max_length=10, choices=Perfil.choices, default=Perfil.CLIENTE)
    is_active = models.BooleanField(default=True, db_column="ativo")
    criado_em = models.DateTimeField(auto_now_add=True)
    departamento = models.ForeignKey(
        Departamento, null=True, blank=True, on_delete=models.SET_NULL, related_name="usuarios"
    )

    objects = UsuarioManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome"]

    class Meta:
        db_table = "usuario"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} <{self.email}>"

    # Propriedades de perfil -------------------------------------------------
    @property
    def eh_cliente(self):
        return self.perfil == self.Perfil.CLIENTE

    @property
    def eh_tecnico(self):
        return self.perfil == self.Perfil.TECNICO

    @property
    def eh_admin(self):
        return self.perfil == self.Perfil.ADMIN

    @property
    def eh_equipe(self):
        """Técnico ou administrador."""
        return self.perfil in (self.Perfil.TECNICO, self.Perfil.ADMIN)

    # Integração com o Django Admin -----------------------------------------
    @property
    def is_staff(self):
        return self.eh_admin

    @property
    def is_superuser(self):
        return self.eh_admin

    def has_perm(self, perm, obj=None):
        return self.is_active and self.eh_admin

    def has_module_perms(self, app_label):
        return self.is_active and self.eh_admin
