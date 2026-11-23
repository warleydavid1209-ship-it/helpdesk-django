from django.urls import path

from . import views

urlpatterns = [
    path("auth/cadastro/", views.CadastroAPIView.as_view(), name="api_cadastro"),
    path("auth/login/", views.LoginAPIView.as_view(), name="api_login"),
    path("auth/logout/", views.LogoutAPIView.as_view(), name="api_logout"),
    path("auth/me/", views.PerfilAPIView.as_view(), name="api_me"),
    path("departamentos/", views.DepartamentoListAPIView.as_view(), name="api_departamentos"),
    path("usuarios/", views.UsuarioListAPIView.as_view(), name="api_usuarios"),
]
