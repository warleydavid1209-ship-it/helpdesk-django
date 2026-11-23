from django.conf import settings
from django.db import models

from usuarios.models import Departamento


class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, default="")
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT, related_name="categorias")

    class Meta:
        db_table = "categoria"
        ordering = ["nome"]
        constraints = [models.UniqueConstraint(fields=["departamento", "nome"], name="uq_categoria_dep_nome")]

    def __str__(self):
        return f"{self.nome} ({self.departamento})"


class Chamado(models.Model):
    class Status(models.TextChoices):
        ABERTO = "aberto", "Aberto"
        EM_ANDAMENTO = "em_andamento", "Em andamento"
        AGUARDANDO = "aguardando", "Aguardando cliente"
        RESOLVIDO = "resolvido", "Resolvido"
        FECHADO = "fechado", "Fechado"

    class Prioridade(models.TextChoices):
        BAIXA = "baixa", "Baixa"
        MEDIA = "media", "Média"
        ALTA = "alta", "Alta"
        CRITICA = "critica", "Crítica"

    titulo = models.CharField(max_length=150)
    descricao = models.TextField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ABERTO)
    prioridade = models.CharField(max_length=10, choices=Prioridade.choices, default=Prioridade.MEDIA)
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="chamados_solicitados"
    )
    tecnico = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="chamados_atendidos"
    )
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="chamados")
    aberto_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    fechado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "chamado"
        ordering = ["-aberto_em"]
        indexes = [
            models.Index(fields=["status"], name="idx_chamado_status"),
            models.Index(fields=["solicitante"], name="idx_chamado_solicitante"),
            models.Index(fields=["tecnico"], name="idx_chamado_tecnico"),
        ]

    def __str__(self):
        return f"#{self.pk} {self.titulo}"


class Comentario(models.Model):
    chamado = models.ForeignKey(Chamado, on_delete=models.CASCADE, related_name="comentarios")
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="comentarios")
    texto = models.TextField()
    interno = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "comentario"
        ordering = ["criado_em"]


class Anexo(models.Model):
    chamado = models.ForeignKey(Chamado, on_delete=models.CASCADE, related_name="anexos")
    enviado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="anexos")
    arquivo = models.FileField(upload_to="anexos/%Y/%m/", max_length=255)
    enviado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "anexo"
        ordering = ["enviado_em"]


class HistoricoStatus(models.Model):
    chamado = models.ForeignKey(Chamado, on_delete=models.CASCADE, related_name="historico")
    alterado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="alteracoes_status"
    )
    status_anterior = models.CharField(max_length=15, blank=True, default="")
    status_novo = models.CharField(max_length=15)
    alterado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "historico_status"
        ordering = ["alterado_em"]
