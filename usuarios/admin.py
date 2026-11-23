from django import forms
from django.contrib import admin

from .models import Departamento, Usuario


class UsuarioAdminForm(forms.ModelForm):
    senha_nova = forms.CharField(
        label="Senha", required=False, widget=forms.PasswordInput(render_value=False),
        help_text="Obrigatória ao criar. Ao editar, deixe em branco para manter a senha atual.",
    )

    class Meta:
        model = Usuario
        fields = ["nome", "email", "perfil", "departamento", "is_active"]

    def clean(self):
        dados = super().clean()
        if not self.instance.pk and not dados.get("senha_nova"):
            self.add_error("senha_nova", "Informe uma senha para o novo usuário.")
        return dados

    def save(self, commit=True):
        usuario = super().save(commit=False)
        if self.cleaned_data.get("senha_nova"):
            usuario.set_password(self.cleaned_data["senha_nova"])
        if commit:
            usuario.save()
        return usuario


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    form = UsuarioAdminForm
    list_display = ("nome", "email", "perfil", "departamento", "is_active")
    list_filter = ("perfil", "is_active", "departamento")
    search_fields = ("nome", "email")
    fieldsets = ((None, {"fields": ("nome", "email", "senha_nova", "perfil", "departamento", "is_active")}),)


admin.site.register(Departamento)
