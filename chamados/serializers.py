from rest_framework import serializers

from usuarios.serializers import UsuarioResumoSerializer

from .models import Anexo, Categoria, Chamado, Comentario, HistoricoStatus
from . import services


class CategoriaSerializer(serializers.ModelSerializer):
    departamento_nome = serializers.CharField(source="departamento.nome", read_only=True)

    class Meta:
        model = Categoria
        fields = ["id", "nome", "descricao", "departamento", "departamento_nome"]


class ComentarioSerializer(serializers.ModelSerializer):
    autor = UsuarioResumoSerializer(read_only=True)

    class Meta:
        model = Comentario
        fields = ["id", "autor", "texto", "interno", "criado_em"]
        read_only_fields = ["id", "autor", "criado_em"]


class AnexoSerializer(serializers.ModelSerializer):
    enviado_por = UsuarioResumoSerializer(read_only=True)

    class Meta:
        model = Anexo
        fields = ["id", "arquivo", "enviado_por", "enviado_em"]


class HistoricoSerializer(serializers.ModelSerializer):
    alterado_por = UsuarioResumoSerializer(read_only=True)

    class Meta:
        model = HistoricoStatus
        fields = ["id", "status_anterior", "status_novo", "alterado_por", "alterado_em"]


class ChamadoListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    prioridade_display = serializers.CharField(source="get_prioridade_display", read_only=True)
    solicitante = UsuarioResumoSerializer(read_only=True)
    tecnico = UsuarioResumoSerializer(read_only=True)
    categoria = CategoriaSerializer(read_only=True)

    class Meta:
        model = Chamado
        fields = [
            "id", "titulo", "descricao", "status", "status_display", "prioridade", "prioridade_display",
            "solicitante", "tecnico", "categoria", "aberto_em", "atualizado_em", "fechado_em",
        ]


class ChamadoDetalheSerializer(ChamadoListSerializer):
    comentarios = serializers.SerializerMethodField()
    anexos = AnexoSerializer(many=True, read_only=True)
    historico = HistoricoSerializer(many=True, read_only=True)

    class Meta(ChamadoListSerializer.Meta):
        fields = ChamadoListSerializer.Meta.fields + ["comentarios", "anexos", "historico"]

    def get_comentarios(self, chamado):
        usuario = self.context["request"].user
        return ComentarioSerializer(services.comentarios_visiveis(chamado, usuario), many=True).data


class ChamadoCriarSerializer(serializers.Serializer):
    """Valida o payload de abertura de chamado."""

    titulo = serializers.CharField(max_length=150)
    descricao = serializers.CharField()
    categoria = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all())
    prioridade = serializers.ChoiceField(choices=Chamado.Prioridade.choices, default=Chamado.Prioridade.MEDIA)

    def validate_titulo(self, valor):
        if len(valor.strip()) < 5:
            raise serializers.ValidationError("O título deve ter pelo menos 5 caracteres.")
        return valor.strip()

    def validate_descricao(self, valor):
        if len(valor.strip()) < 10:
            raise serializers.ValidationError("A descrição deve ter pelo menos 10 caracteres.")
        return valor.strip()


class StatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Chamado.Status.choices)


class PrioridadeSerializer(serializers.Serializer):
    prioridade = serializers.ChoiceField(choices=Chamado.Prioridade.choices)


class AtribuirSerializer(serializers.Serializer):
    tecnico_id = serializers.IntegerField()


class ComentarioCriarSerializer(serializers.Serializer):
    texto = serializers.CharField()
    interno = serializers.BooleanField(default=False)


class AnexoCriarSerializer(serializers.Serializer):
    arquivo = serializers.FileField()
