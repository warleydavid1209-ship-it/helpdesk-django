from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from chamados import web
from usuarios.forms import LoginForm

urlpatterns = [
    path("admin/", admin.site.urls),
    # API REST
    path("api/", include("usuarios.urls")),
    path("api/", include("chamados.api_urls")),
    # Telas
    path("", web.chamado_lista, name="chamado_lista"),
    path("login/", auth_views.LoginView.as_view(template_name="usuarios/login.html", authentication_form=LoginForm), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("cadastro/", web.cadastro, name="cadastro"),
    path("chamados/novo/", web.chamado_novo, name="chamado_novo"),
    path("chamados/<int:pk>/", web.chamado_detalhe, name="chamado_detalhe"),
    path("dashboard/", web.dashboard, name="dashboard"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
