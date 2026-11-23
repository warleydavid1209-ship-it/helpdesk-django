from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Departamento, Usuario


class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = ["id", "nome", "descricao"]


class UsuarioSerializer(serializers.ModelSerializer):
    perfil_display = serializers.CharField(source="get_perfil_display", read_only=True)

    class Meta:
        model = Usuario
        fields = ["id", "nome", "email", "perfil", "perfil_display", "departamento", "criado_em"]


class UsuarioResumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["id", "nome"]


class CadastroSerializer(serializers.ModelSerializer):
    """Auto-cadastro público: sempre cria um usuário com perfil CLIENTE."""

    senha = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = Usuario
        fields = ["id", "nome", "email", "senha", "departamento"]

    def validate_nome(self, valor):
        valor = valor.strip()
        if len(valor) < 3:
            raise serializers.ValidationError("Informe o nome completo (mínimo 3 caracteres).")
        return valor

    def validate_email(self, valor):
        valor = valor.strip().lower()
        if Usuario.objects.filter(email__iexact=valor).exists():
            raise serializers.ValidationError("Já existe um usuário com este e-mail.")
        return valor

    def validate_senha(self, valor):
        validate_password(valor)
        return valor

    def create(self, dados):
        senha = dados.pop("senha")
        return Usuario.objects.create_user(password=senha, perfil=Usuario.Perfil.CLIENTE, **dados)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    senha = serializers.CharField(style={"input_type": "password"})
