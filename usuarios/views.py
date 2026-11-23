from django.contrib.auth import authenticate
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Departamento, Usuario
from .serializers import (
    CadastroSerializer, DepartamentoSerializer, LoginSerializer, UsuarioSerializer,
)


class CadastroAPIView(generics.CreateAPIView):
    """POST /api/auth/cadastro/ - cria um usuário cliente."""

    serializer_class = CadastroSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        usuario = ser.save()
        return Response(UsuarioSerializer(usuario).data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    """POST /api/auth/login/ - devolve o token de acesso."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        usuario = authenticate(request, email=ser.validated_data["email"].lower(), password=ser.validated_data["senha"])
        if usuario is None:
            return Response({"detail": "E-mail ou senha inválidos."}, status=status.HTTP_401_UNAUTHORIZED)
        token, _ = Token.objects.get_or_create(user=usuario)
        return Response({"token": token.key, "usuario": UsuarioSerializer(usuario).data})


class LogoutAPIView(APIView):
    """POST /api/auth/logout/ - invalida o token atual."""

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PerfilAPIView(APIView):
    """GET /api/auth/me/ - dados do usuário logado."""

    def get(self, request):
        return Response(UsuarioSerializer(request.user).data)


class DepartamentoListAPIView(generics.ListAPIView):
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer
    pagination_class = None


class UsuarioListAPIView(generics.ListAPIView):
    """GET /api/usuarios/?perfil=tecnico - lista de usuários (somente equipe)."""

    serializer_class = UsuarioSerializer

    def get_queryset(self):
        if not self.request.user.eh_equipe:
            return Usuario.objects.none()
        qs = Usuario.objects.filter(is_active=True)
        perfil = self.request.query_params.get("perfil")
        return qs.filter(perfil=perfil) if perfil else qs
