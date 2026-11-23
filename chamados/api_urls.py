from django.urls import path

from . import views

urlpatterns = [
    path("categorias/", views.CategoriaListAPIView.as_view(), name="api_categorias"),
    path("chamados/", views.ChamadoListCreateAPIView.as_view(), name="api_chamados"),
    path("chamados/<int:pk>/", views.ChamadoDetalheAPIView.as_view(), name="api_chamado_detalhe"),
    path("chamados/<int:pk>/status/", views.ChamadoStatusAPIView.as_view(), name="api_chamado_status"),
    path("chamados/<int:pk>/assumir/", views.ChamadoAssumirAPIView.as_view(), name="api_chamado_assumir"),
    path("chamados/<int:pk>/atribuir/", views.ChamadoAtribuirAPIView.as_view(), name="api_chamado_atribuir"),
    path("chamados/<int:pk>/comentarios/", views.ChamadoComentariosAPIView.as_view(), name="api_chamado_comentarios"),
    path("chamados/<int:pk>/anexos/", views.ChamadoAnexosAPIView.as_view(), name="api_chamado_anexos"),
    path("dashboard/", views.DashboardAPIView.as_view(), name="api_dashboard"),
]
