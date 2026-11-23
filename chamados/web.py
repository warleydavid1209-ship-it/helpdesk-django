"""Telas (HTML) do sistema. Usam a mesma camada de serviços da API."""
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
import csv

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from usuarios.forms import CadastroForm
from usuarios.models import Usuario

from . import services
from .forms import ChamadoForm
from .models import Categoria, Chamado


def cadastro(request):
    if request.user.is_authenticated:
        return redirect("chamado_lista")
    form = CadastroForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        login(request, usuario)
        messages.success(request, "Conta criada com sucesso! Bem-vindo(a).")
        return redirect("chamado_lista")
    return render(request, "usuarios/cadastro.html", {"form": form})


@login_required
def chamado_lista(request):
    qs = services.chamados_visiveis(request.user)
    f = {k: request.GET.get(k, "").strip() for k in ("status", "prioridade", "categoria", "q", "escopo")}
    if f["status"]:
        qs = qs.filter(status=f["status"])
    if f["prioridade"]:
        qs = qs.filter(prioridade=f["prioridade"])
    if f["categoria"].isdigit():
        qs = qs.filter(categoria_id=int(f["categoria"]))
    if f["q"]:
        qs = qs.filter(titulo__icontains=f["q"])
    if request.user.eh_equipe:
        if f["escopo"] == "sem_tecnico":
            qs = qs.filter(tecnico__isnull=True).exclude(status=Chamado.Status.FECHADO)
        elif f["escopo"] == "meus":
            qs = qs.filter(tecnico=request.user)
    ctx = {"chamados": qs[:100], "f": f, "status_opcoes": Chamado.Status.choices,
           "prioridade_opcoes": Chamado.Prioridade.choices,
           "categorias": Categoria.objects.all()}
    return render(request, "chamados/lista.html", ctx)


@login_required
def chamado_novo(request):
    form = ChamadoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        d = form.cleaned_data
        try:
            chamado = services.abrir_chamado(request.user, d["titulo"], d["descricao"], d["categoria"], d["prioridade"])
            if d.get("arquivo"):
                services.anexar(chamado, request.user, d["arquivo"])
        except services.RegraNegocioError as erro:
            form.add_error(None, str(erro))
        else:
            messages.success(request, f"Chamado #{chamado.pk} aberto com sucesso!")
            return redirect("chamado_detalhe", pk=chamado.pk)
    return render(request, "chamados/novo.html", {"form": form})


@login_required
def chamado_detalhe(request, pk):
    chamado = get_object_or_404(services.chamados_visiveis(request.user), pk=pk)
    if request.method == "POST":
        acao = request.POST.get("acao")
        try:
            if acao == "comentar":
                services.comentar(chamado, request.user, request.POST.get("texto"), request.POST.get("interno") == "on")
                messages.success(request, "Comentário registrado.")
            elif acao == "status":
                services.alterar_status(chamado, request.user, request.POST.get("status"))
                messages.success(request, "Status atualizado.")
            elif acao == "prioridade":
                services.alterar_prioridade(chamado, request.user, request.POST.get("prioridade"))
                messages.success(request, "Prioridade atualizada.")
            elif acao == "assumir":
                services.assumir_chamado(chamado, request.user)
                messages.success(request, "Você assumiu este chamado.")
            elif acao == "atribuir":
                tecnico = get_object_or_404(Usuario, pk=request.POST.get("tecnico") or 0)
                services.atribuir_tecnico(chamado, request.user, tecnico)
                messages.success(request, f"Chamado atribuído a {tecnico.nome}.")
            elif acao == "anexar" and request.FILES.get("arquivo"):
                services.anexar(chamado, request.user, request.FILES["arquivo"])
                messages.success(request, "Arquivo anexado.")
            else:
                messages.error(request, "Ação inválida.")
        except services.RegraNegocioError as erro:
            messages.error(request, str(erro))
        except services.SemPermissaoError as erro:
            messages.error(request, str(erro))
        return redirect("chamado_detalhe", pk=chamado.pk)
    ctx = {
        "chamado": chamado,
        "comentarios": services.comentarios_visiveis(chamado, request.user),
        "historico": chamado.historico.select_related("alterado_por"),
        "anexos": chamado.anexos.all(),
        "proximos_status": [(v, Chamado.Status(v).label) for v in services.TRANSICOES[chamado.status]],
        "tecnicos": Usuario.objects.filter(perfil=Usuario.Perfil.TECNICO, is_active=True),
        "prioridade_opcoes": Chamado.Prioridade.choices,
    }
    return render(request, "chamados/detalhe.html", ctx)


@login_required
def dashboard(request):
    if not request.user.eh_equipe:
        raise Http404()
    dados = services.indicadores()
    status_labels = dict(Chamado.Status.choices)
    prio_labels = dict(Chamado.Prioridade.choices)
    ctx = {
        "total": dados["total"], "sem_tecnico": dados["sem_tecnico"],
        "por_status": [(status_labels[k], v) for k, v in dados["por_status"].items()],
        "por_prioridade": [(prio_labels[k], v) for k, v in dados["por_prioridade"].items()],
        "por_categoria": list(dados["por_categoria"].items()),
    }
    return render(request, "chamados/dashboard.html", ctx)


@login_required
def exportar_csv(request):
    """Relatório: exporta a lista de chamados (respeitando os filtros) em CSV, para a equipe."""
    if not request.user.eh_equipe:
        raise Http404()
    qs = services.chamados_visiveis(request.user)
    if request.GET.get("status"):
        qs = qs.filter(status=request.GET["status"])
    if request.GET.get("prioridade"):
        qs = qs.filter(prioridade=request.GET["prioridade"])
    resposta = HttpResponse(content_type="text/csv; charset=utf-8")
    resposta["Content-Disposition"] = 'attachment; filename="chamados.csv"'
    resposta.write("\ufeff")  # BOM: o Excel abre os acentos corretamente
    w = csv.writer(resposta, delimiter=";")
    w.writerow(["ID", "Título", "Categoria", "Prioridade", "Status", "Solicitante", "Técnico", "Aberto em", "Fechado em"])
    for c in qs.order_by("id"):
        w.writerow([c.pk, c.titulo, c.categoria.nome, c.get_prioridade_display(), c.get_status_display(),
                    c.solicitante.nome, c.tecnico.nome if c.tecnico else "",
                    c.aberto_em.strftime("%d/%m/%Y %H:%M"), c.fechado_em.strftime("%d/%m/%Y %H:%M") if c.fechado_em else ""])
    return resposta


@login_required
def gerenciar(request):
    """Cadastro de categorias e departamentos (RF09) para o administrador."""
    if not request.user.eh_admin:
        raise Http404()
    from usuarios.models import Departamento

    if request.method == "POST":
        acao = request.POST.get("acao")
        nome = (request.POST.get("nome") or "").strip()
        try:
            if len(nome) < 3:
                raise ValueError("Informe um nome com pelo menos 3 caracteres.")
            if acao == "departamento":
                if Departamento.objects.filter(nome__iexact=nome).exists():
                    raise ValueError("Já existe um departamento com esse nome.")
                Departamento.objects.create(nome=nome, descricao=request.POST.get("descricao", "").strip())
                messages.success(request, f"Departamento \"{nome}\" criado.")
            elif acao == "categoria":
                dep = Departamento.objects.filter(pk=request.POST.get("departamento") or 0).first()
                if not dep:
                    raise ValueError("Selecione o departamento da categoria.")
                if Categoria.objects.filter(departamento=dep, nome__iexact=nome).exists():
                    raise ValueError("Esse departamento já tem uma categoria com esse nome.")
                Categoria.objects.create(nome=nome, departamento=dep, descricao=request.POST.get("descricao", "").strip())
                messages.success(request, f"Categoria \"{nome}\" criada.")
        except ValueError as erro:
            messages.error(request, str(erro))
        return redirect("gerenciar")
    return render(request, "chamados/gerenciar.html", {
        "departamentos": Departamento.objects.all(),
        "categorias": Categoria.objects.select_related("departamento"),
    })
