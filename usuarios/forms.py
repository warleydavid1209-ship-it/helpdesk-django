from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password

from .models import Usuario


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="E-mail", widget=forms.EmailInput(attrs={"class": "form-control", "autofocus": True}))
    password = forms.CharField(label="Senha", widget=forms.PasswordInput(attrs={"class": "form-control"}))
    error_messages = {"invalid_login": "E-mail ou senha inválidos.", "inactive": "Esta conta está inativa."}


class CadastroForm(forms.ModelForm):
    senha = forms.CharField(label="Senha", widget=forms.PasswordInput(attrs={"class": "form-control"}))
    confirmar_senha = forms.CharField(label="Confirmar senha", widget=forms.PasswordInput(attrs={"class": "form-control"}))

    class Meta:
        model = Usuario
        fields = ["nome", "email", "departamento"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "departamento": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Já existe um usuário com este e-mail.")
        return email

    def clean(self):
        dados = super().clean()
        senha, conf = dados.get("senha"), dados.get("confirmar_senha")
        if senha:
            validate_password(senha)
            if conf != senha:
                self.add_error("confirmar_senha", "As senhas não conferem.")
        return dados

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.perfil = Usuario.Perfil.CLIENTE
        usuario.set_password(self.cleaned_data["senha"])
        if commit:
            usuario.save()
        return usuario
