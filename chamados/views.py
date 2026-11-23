"""API REST de chamados (Django REST Framework)."""
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.models import Usuario

from . import services
from .models import Categoria, Chamado
from .serializers import (
    AnexoCriarSerializer, AnexoSerializer, AtribuirSerializer, CategoriaSerializer,
    ChamadoCriarSerializer, ChamadoDetalheSerializer, ChamadoListSerializer,
    ComentarioCriarSerializer, ComentarioSerializer, PrioridadeSerializer, StatusSerializer,
)


class RegrasMixin:
    """Converte as exceções de negócio em respostas HTTP adequadas."""

    def handle_exception(self, exc):
        if isinstance(exc, services.RegraNegocioError):
            exc = ValidationError({"detail": str(exc)})
        elif isinstance(exc, services.SemPermissaoError):
            exc = PermissionDenied(str(exc))
        return super().handle_exception(exc)

    def get_chamado(self, pk):
        return get_object_or_404(services.chamados_visiveis(self.request.user), pk=pk)


class CategoriaListAPIView(generics.ListAPIView):
    queryset = Categoria.objects.select_related("departamento")
    serializer_class = CategoriaSerializer
    pagination_class = None


class ChamadoListCreateAPIView(RegrasMixin, generics.ListCreateAPIView):
    """GET  /api/chamados/  - lista (filtros: status, prioridade, categoria, q, sem_tecnico, meus)
    POST /api/chamados/  - abre um chamado."""

    def get_serializer_class(self):
        return ChamadoCriarSerializer if self.request.method == "POST" else ChamadoListSerializer

    def get_queryset(self):
        usuario = self.request.user
        qs = services.chamados_visiveis(usuario)
        p = self.request.query_params
        if p.get("status"):
            qs = qs.filter(status=p["status"])
        if p.get("prioridade"):
            qs = qs.filter(prioridade=p["prioridade"])
        if p.get("categoria"):
            qs = qs.filter(categoria_id=p["categoria"])
        if p.get("q"):
            qs = qs.filter(Q(titulo__icontains=p["q"]) | Q(descricao__icontains=p["q"]))
        if usuario.eh_equipe:
            if p.get("sem_tecnico") in ("1", "true"):
                qs = qs.filter(tecnico__isnull=True)
            if p.get("meus") in ("1", "true"):
                qs = qs.filter(tecnico=usuario)
        return qs

    def create(self, request, *args, **kwargs):
        ser = ChamadoCriarSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        chamado = services.abrir_chamado(request.user, **ser.validated_data)
        return Response(ChamadoDetalheSerializer(chamado, context={"request": request}).data,
                        status=status.HTTP_201_CREATED)


class ChamadoDetalheAPIView(RegrasMixin, APIView):
    """GET /api/chamados/<id>/ - detalhe | PATCH - altera a prioridade (equipe)."""

    def get(self, request, pk):
        chamado = self.get_chamado(pk)
        return Response(ChamadoDetalheSerializer(chamado, context={"request": request}).data)

    def patch(self, request, pk):
        chamado = self.get_chamado(pk)
        ser = PrioridadeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        services.alterar_prioridade(chamado, request.user, ser.validated_data["prioridade"])
        return Response(ChamadoDetalheSerializer(chamado, context={"request": request}).data)


class ChamadoStatusAPIView(RegrasMixin, APIView):
    """POST /api/chamados/<id>/status/  {"status": "resolvido"}"""

    def post(self, request, pk):
        chamado = self.get_chamado(pk)
        ser = StatusSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        services.alterar_status(chamado, request.user, ser.validated_data["status"])
        return Response(ChamadoDetalheSerializer(chamado, context={"request": request}).data)


class ChamadoAssumirAPIView(RegrasMixin, APIView):
    """POST /api/chamados/<id>/assumir/"""

    def post(self, request, pk):
        chamado = self.get_chamado(pk)
        services.assumir_chamado(chamado, request.user)
        return Response(ChamadoDetalheSerializer(chamado, context={"request": request}).data)


class ChamadoAtribuirAPIView(RegrasMixin, APIView):
    """POST /api/chamados/<id>/atribuir/  {"tecnico_id": 2}  (administrador)"""

    def post(self, request, pk):
        chamado = self.get_chamado(pk)
        ser = AtribuirSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        tecnico = Usuario.objects.filter(pk=ser.validated_data["tecnico_id"]).first()
        if tecnico is None:
            raise ValidationError({"tecnico_id": "Técnico não encontrado."})
        services.atribuir_tecnico(chamado, request.user, tecnico)
        return Response(ChamadoDetalheSerializer(chamado, context={"request": request}).data)


class ChamadoComentariosAPIView(RegrasMixin, APIView):
    """GET/POST /api/chamados/<id>/comentarios/"""

    def get(self, request, pk):
        chamado = self.get_chamado(pk)
        dados = services.comentarios_visiveis(chamado, request.user)
        return Response(ComentarioSerializer(dados, many=True).data)

    def post(self, request, pk):
        chamado = self.get_chamado(pk)
        ser = ComentarioCriarSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        comentario = services.comentar(chamado, request.user, **ser.validated_data)
        return Response(ComentarioSerializer(comentario).data, status=status.HTTP_201_CREATED)


class ChamadoAnexosAPIView(RegrasMixin, APIView):
    """POST /api/chamados/<id>/anexos/  (multipart/form-data, campo "arquivo")"""

    def post(self, request, pk):
        chamado = self.get_chamado(pk)
        ser = AnexoCriarSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        anexo = services.anexar(chamado, request.user, ser.validated_data["arquivo"])
        return Response(AnexoSerializer(anexo).data, status=status.HTTP_201_CREATED)


class DashboardAPIView(RegrasMixin, APIView):
    """GET /api/dashboard/ - indicadores (técnico e administrador)."""

    def get(self, request):
        if not request.user.eh_equipe:
            raise services.SemPermissaoError("Apenas a equipe acessa os indicadores.")
        return Response(services.indicadores())
