"""Regras de negócio do Help Desk.

Esta camada é usada tanto pela API (DRF) quanto pelas telas (templates),
garantindo que as mesmas validações valham nos dois caminhos.
"""
import os

from django.db import transaction
from django.utils import timezone

from usuarios.models import Usuario

from .models import Anexo, Chamado, Comentario, HistoricoStatus

S = Chamado.Status

# Transições de status permitidas
TRANSICOES = {
    S.ABERTO: {S.EM_ANDAMENTO, S.FECHADO},
    S.EM_ANDAMENTO: {S.AGUARDANDO, S.RESOLVIDO, S.FECHADO},
    S.AGUARDANDO: {S.EM_ANDAMENTO, S.RESOLVIDO, S.FECHADO},
    S.RESOLVIDO: {S.FECHADO, S.EM_ANDAMENTO},
    S.FECHADO: set(),
}

EXTENSOES_PERMITIDAS = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".txt", ".log", ".docx", ".xlsx"}
TAMANHO_MAX_ANEXO = 5 * 1024 * 1024  # 5 MB


class RegraNegocioError(Exception):
    """Violação de regra de negócio (vira HTTP 400 na API e mensagem na tela)."""


class SemPermissaoError(Exception):
    """Usuário sem permissão para a ação (vira HTTP 403)."""


def chamados_visiveis(usuario):
    """Cliente vê só os próprios chamados; técnico e admin veem todos."""
    qs = Chamado.objects.select_related("solicitante", "tecnico", "categoria", "categoria__departamento")
    if usuario.eh_equipe:
        return qs
    return qs.filter(solicitante=usuario)


def _registrar_historico(chamado, usuario, anterior, novo):
    HistoricoStatus.objects.create(
        chamado=chamado, alterado_por=usuario, status_anterior=anterior, status_novo=novo
    )


@transaction.atomic
def abrir_chamado(usuario, titulo, descricao, categoria, prioridade=Chamado.Prioridade.MEDIA):
    titulo = (titulo or "").strip()
    descricao = (descricao or "").strip()
    if len(titulo) < 5:
        raise RegraNegocioError("O título deve ter pelo menos 5 caracteres.")
    if len(descricao) < 10:
        raise RegraNegocioError("A descrição deve ter pelo menos 10 caracteres.")
    chamado = Chamado.objects.create(
        titulo=titulo, descricao=descricao, categoria=categoria,
        prioridade=prioridade, solicitante=usuario, status=S.ABERTO,
    )
    _registrar_historico(chamado, usuario, "", S.ABERTO)
    return chamado


@transaction.atomic
def alterar_status(chamado, usuario, novo_status):
    if not usuario.eh_equipe:
        raise SemPermissaoError("Apenas técnicos e administradores alteram o status.")
    if novo_status not in Chamado.Status.values:
        raise RegraNegocioError(f"Status inválido: {novo_status}.")
    atual = chamado.status
    if novo_status == atual:
        raise RegraNegocioError("O chamado já está com esse status.")
    if novo_status not in TRANSICOES[atual]:
        raise RegraNegocioError(
            f"Transição não permitida: {Chamado.Status(atual).label} → {Chamado.Status(novo_status).label}."
        )
    chamado.status = novo_status
    chamado.fechado_em = timezone.now() if novo_status == S.FECHADO else None
    chamado.save()
    _registrar_historico(chamado, usuario, atual, novo_status)
    return chamado


@transaction.atomic
def assumir_chamado(chamado, usuario):
    if not usuario.eh_equipe:
        raise SemPermissaoError("Apenas técnicos e administradores assumem chamados.")
    if chamado.status == S.FECHADO:
        raise RegraNegocioError("Chamado fechado não pode ser assumido.")
    if chamado.tecnico_id and chamado.tecnico_id != usuario.id:
        raise RegraNegocioError(f"O chamado já está com {chamado.tecnico.nome}.")
    anterior = chamado.status
    chamado.tecnico = usuario
    if anterior == S.ABERTO:
        chamado.status = S.EM_ANDAMENTO
    chamado.save()
    if anterior != chamado.status:
        _registrar_historico(chamado, usuario, anterior, chamado.status)
    return chamado


@transaction.atomic
def atribuir_tecnico(chamado, usuario, tecnico):
    if not usuario.eh_admin:
        raise SemPermissaoError("Apenas administradores atribuem técnicos.")
    if tecnico.perfil != Usuario.Perfil.TECNICO or not tecnico.is_active:
        raise RegraNegocioError("O usuário informado não é um técnico ativo.")
    if chamado.status == S.FECHADO:
        raise RegraNegocioError("Chamado fechado não pode receber técnico.")
    anterior = chamado.status
    chamado.tecnico = tecnico
    if anterior == S.ABERTO:
        chamado.status = S.EM_ANDAMENTO
    chamado.save()
    if anterior != chamado.status:
        _registrar_historico(chamado, usuario, anterior, chamado.status)
    return chamado


def alterar_prioridade(chamado, usuario, prioridade):
    if not usuario.eh_equipe:
        raise SemPermissaoError("Apenas técnicos e administradores alteram a prioridade.")
    if prioridade not in Chamado.Prioridade.values:
        raise RegraNegocioError(f"Prioridade inválida: {prioridade}.")
    chamado.prioridade = prioridade
    chamado.save()
    return chamado


def comentarios_visiveis(chamado, usuario):
    qs = chamado.comentarios.select_related("autor")
    return qs if usuario.eh_equipe else qs.filter(interno=False)


def comentar(chamado, autor, texto, interno=False):
    texto = (texto or "").strip()
    if len(texto) < 2:
        raise RegraNegocioError("O comentário não pode ser vazio.")
    if chamado.status == S.FECHADO:
        raise RegraNegocioError("Chamado fechado não aceita novos comentários.")
    if interno and not autor.eh_equipe:
        raise SemPermissaoError("Apenas a equipe pode criar notas internas.")
    return Comentario.objects.create(chamado=chamado, autor=autor, texto=texto, interno=bool(interno))


def anexar(chamado, usuario, arquivo):
    if chamado.status == S.FECHADO:
        raise RegraNegocioError("Chamado fechado não aceita anexos.")
    ext = os.path.splitext(arquivo.name)[1].lower()
    if ext not in EXTENSOES_PERMITIDAS:
        raise RegraNegocioError(f"Tipo de arquivo não permitido ({ext or 'sem extensão'}).")
    if arquivo.size > TAMANHO_MAX_ANEXO:
        raise RegraNegocioError("O arquivo excede o limite de 5 MB.")
    return Anexo.objects.create(chamado=chamado, enviado_por=usuario, arquivo=arquivo)


def indicadores():
    from django.db.models import Count

    def contagem(campo, choices):
        dados = dict(Chamado.objects.values_list(campo).annotate(t=Count("id")))
        return {valor: dados.get(valor, 0) for valor, _ in choices.choices}

    return {
        "total": Chamado.objects.count(),
        "por_status": contagem("status", Chamado.Status),
        "por_prioridade": contagem("prioridade", Chamado.Prioridade),
        "sem_tecnico": Chamado.objects.filter(tecnico__isnull=True).exclude(status=S.FECHADO).count(),
    }
