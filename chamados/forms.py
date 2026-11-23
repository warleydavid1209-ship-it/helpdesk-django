from django import forms

from .models import Categoria, Chamado


class ChamadoForm(forms.Form):
    titulo = forms.CharField(label="Título", max_length=150, min_length=5,
                             widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Resumo do problema"}))
    categoria = forms.ModelChoiceField(label="Categoria", queryset=Categoria.objects.select_related("departamento"),
                                       empty_label="Selecione...", widget=forms.Select(attrs={"class": "form-select"}))
    prioridade = forms.ChoiceField(label="Prioridade", choices=Chamado.Prioridade.choices, initial=Chamado.Prioridade.MEDIA,
                                   widget=forms.Select(attrs={"class": "form-select"}))
    descricao = forms.CharField(label="Descrição", min_length=10,
                                widget=forms.Textarea(attrs={"class": "form-control", "rows": 5,
                                                             "placeholder": "Descreva o problema com o máximo de detalhes"}))
    arquivo = forms.FileField(label="Anexo (opcional)", required=False,
                              widget=forms.ClearableFileInput(attrs={"class": "form-control"}))
