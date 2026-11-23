"""Gera os wireframes (baixa fidelidade) das telas do Help Desk em PNG e PDF."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, Rectangle

plt.rcParams["font.family"] = "DejaVu Sans"
G1, G2, G3, G4, INK = "#F4F5F6", "#E1E4E7", "#C5CAD0", "#8A929B", "#2B2F33"
ACC = "#1565C0"


def tela(titulo, rota, template, logado=True, perfil="Cliente"):
    fig, ax = plt.subplots(figsize=(12, 8.4))
    ax.set_xlim(0, 100); ax.set_ylim(0, 70); ax.invert_yaxis(); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 100, 70, fc="white", ec="none"))
    ax.text(1, -1.8, titulo, fontsize=15, fontweight="bold", color=INK, va="bottom")
    ax.text(99, -1.8, f"Rota: {rota}   |   Template: {template}", fontsize=8.5, color=G4, ha="right", va="bottom")
    ax.add_patch(FancyBboxPatch((1, 2), 98, 66, boxstyle="round,pad=0.2,rounding_size=1", fc="white", ec=G4, lw=1.4))
    ax.add_patch(Rectangle((1, 2), 98, 4, fc=G2, ec=G4, lw=1.0))
    for i in range(3):
        ax.add_patch(plt.Circle((3 + i * 1.6, 4), 0.55, fc=G3, ec=G4, lw=.6))
    ax.add_patch(FancyBboxPatch((11, 2.9), 60, 2.2, boxstyle="round,pad=0,rounding_size=1", fc="white", ec=G3, lw=.8))
    ax.text(12, 4.0, "https://helpdesk.exemplo.com" + rota.split(" ")[0], fontsize=7.5, color=G4, va="center")
    if logado:
        ax.add_patch(Rectangle((1, 6), 98, 5, fc=INK, ec="none"))
        ax.text(3, 8.5, "Help Desk", color="white", fontsize=10, va="center", fontweight="bold")
        ax.text(17, 8.5, "Chamados      Novo chamado" + ("      Dashboard" if perfil != "Cliente" else ""), color="#DDD", fontsize=8.5, va="center")
        ax.text(91.5, 8.5, f"Nome do usuário · {perfil}", color="#DDD", fontsize=8, va="center", ha="right")
        ax.add_patch(FancyBboxPatch((93, 7.2), 5, 2.6, boxstyle="round,pad=0,rounding_size=.5", fc="none", ec="white", lw=.8))
        ax.text(95.5, 8.5, "Sair", color="white", fontsize=7.5, ha="center", va="center")
    return fig, ax


def campo(ax, x, y, w, rotulo, h=3.2, valor="", area=False):
    ax.text(x, y - 0.6, rotulo, fontsize=8.5, color=INK, va="bottom")
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=.4", fc=G1, ec=G3, lw=1))
    if valor:
        ax.text(x + 1, y + h / 2, valor, fontsize=8, color=G4, va="center")


def botao(ax, x, y, w, texto, primario=True, h=3.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=.5", fc=ACC if primario else "white", ec=ACC if primario else G4, lw=1))
    ax.text(x + w / 2, y + h / 2, texto, fontsize=8.5, color="white" if primario else INK, ha="center", va="center", fontweight="bold")


def card(ax, x, y, w, h, titulo=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=.6", fc="white", ec=G3, lw=1.1))
    if titulo:
        ax.text(x + 1.2, y + 1.8, titulo, fontsize=9, fontweight="bold", color=INK, va="center")


def badge(ax, x, y, texto, cor):
    ax.add_patch(FancyBboxPatch((x, y), len(texto) * .75 + 1.6, 2.2, boxstyle="round,pad=0,rounding_size=.9", fc=cor, ec="none"))
    ax.text(x + (len(texto) * .75 + 1.6) / 2, y + 1.1, texto, fontsize=7, color="white", ha="center", va="center")


def nota(ax, x, y, texto):
    ax.text(x, y, texto, fontsize=7.5, color="#B71C1C", style="italic", va="center")


def rodape(ax, txt):
    ax.text(50, 69.6, txt, fontsize=8, color=G4, ha="center", va="center")


def login():
    fig, ax = tela("Tela 1 — Login", "/login/", "usuarios/login.html", logado=False)
    card(ax, 32, 14, 36, 36)
    ax.text(50, 19, "Entrar no Help Desk", fontsize=12, fontweight="bold", color=INK, ha="center")
    campo(ax, 35, 25, 30, "E-mail", valor="seu@email.com"); campo(ax, 35, 33, 30, "Senha", valor="••••••••")
    botao(ax, 35, 40, 30, "Entrar")
    ax.text(50, 46.5, "Não tem conta?  Cadastre-se", fontsize=8, color=ACC, ha="center")
    nota(ax, 70, 27, "← erro: \"E-mail ou senha inválidos\"")
    rodape(ax, "RF01 — Autenticação · API equivalente: POST /api/auth/login/")
    return fig


def cadastro():
    fig, ax = tela("Tela 2 — Cadastro de conta (cliente)", "/cadastro/", "usuarios/cadastro.html", logado=False)
    card(ax, 30, 12, 40, 50)
    ax.text(50, 17, "Criar conta", fontsize=12, fontweight="bold", color=INK, ha="center")
    campo(ax, 33, 23, 34, "Nome completo"); campo(ax, 33, 30, 34, "E-mail"); campo(ax, 33, 37, 34, "Departamento", valor="Selecione...  ▾")
    campo(ax, 33, 44, 16, "Senha"); campo(ax, 51, 44, 16, "Confirmar senha")
    botao(ax, 33, 51, 34, "Cadastrar")
    ax.text(50, 57.5, "Já tem conta?  Entrar", fontsize=8, color=ACC, ha="center")
    nota(ax, 71, 31, "← \"Já existe usuário com este e-mail\"")
    rodape(ax, "RF01/RF09 — Cadastro (sempre perfil Cliente) · API: POST /api/auth/cadastro/")
    return fig


def lista():
    fig, ax = tela("Tela 3 — Lista de chamados / Fila", "/", "chamados/lista.html", perfil="Técnico")
    ax.text(3, 14.5, "Fila de chamados", fontsize=12, fontweight="bold", color=INK, va="center"); botao(ax, 83, 12.8, 14, "+ Novo chamado")
    campo(ax, 3, 18, 28, "", valor="Buscar por título"); campo(ax, 33, 18, 15, "", valor="Status  ▾"); campo(ax, 50, 18, 15, "", valor="Prioridade  ▾")
    campo(ax, 67, 18, 17, "", valor="Escopo  ▾"); botao(ax, 86, 18, 11, "Filtrar", primario=False)
    card(ax, 3, 23, 94, 42)
    ax.add_patch(Rectangle((3, 23), 94, 3.4, fc=G2, ec=G3, lw=.8))
    for x, t in [(4.5, "#"), (8, "Título"), (36, "Categoria"), (50, "Prioridade"), (62, "Status"), (74, "Solicitante"), (86, "Técnico")]:
        ax.text(x, 24.7, t, fontsize=8, fontweight="bold", color=INK, va="center")
    linhas = [("1", "Computador não liga", "Hardware", "Alta", "Em andamento", "#E65100", "Ana Cliente", "Carlos"),
              ("2", "Instalar pacote Office", "Software", "Média", "Aberto", "#1565C0", "João Cliente", "—"),
              ("3", "Wi-Fi caindo na sala 2", "Rede", "Média", "Aguardando", "#6A1B9A", "Ana Cliente", "Carlos"),
              ("6", "Sistema fora do ar", "Rede", "Crítica", "Aberto", "#1565C0", "João Cliente", "—"),
              ("5", "Ar-condicionado vazando", "Climatização", "Alta", "Fechado", "#546E7A", "Ana Cliente", "Marina")]
    for i, (n, t, c, p, s, cor, sol, tec) in enumerate(linhas):
        y = 28.2 + i * 6.8
        ax.plot([3, 97], [y + 3.4, y + 3.4], color=G2, lw=.8)
        ax.text(4.5, y, n, fontsize=8, va="center", color=INK); ax.text(8, y, t, fontsize=8, va="center", color=ACC)
        ax.text(36, y, c, fontsize=8, va="center", color=INK); ax.text(50, y, p, fontsize=8, va="center", color=INK)
        badge(ax, 62, y - 1.1, s, cor); ax.text(74, y, sol, fontsize=8, va="center", color=INK); ax.text(86, y, tec, fontsize=8, va="center", color=INK)
    nota(ax, 3, 66.5, "Cliente vê só os próprios chamados e não vê as colunas Solicitante/Técnico/Escopo.")
    rodape(ax, "RF04 — Listagem com filtros · API: GET /api/chamados/?status=&prioridade=&q=&sem_tecnico=1")
    return fig


def novo():
    fig, ax = tela("Tela 4 — Abrir novo chamado", "/chamados/novo/", "chamados/novo.html")
    ax.text(20, 15, "Abrir novo chamado", fontsize=12, fontweight="bold", color=INK, va="center")
    card(ax, 20, 18, 60, 46)
    campo(ax, 23, 23, 54, "Título", valor="Resumo do problema")
    campo(ax, 23, 31, 33, "Categoria", valor="Selecione...  ▾"); campo(ax, 58, 31, 19, "Prioridade", valor="Média  ▾")
    campo(ax, 23, 39, 54, "Descrição", h=9, valor="Descreva o problema com o máximo de detalhes")
    campo(ax, 23, 52, 54, "Anexo (opcional)", valor="Escolher arquivo…   nenhum arquivo selecionado")
    botao(ax, 23, 58, 18, "Abrir chamado"); botao(ax, 43, 58, 14, "Cancelar", primario=False)
    nota(ax, 81, 24.5, "← título ≥ 5 caracteres"); nota(ax, 81, 43, "← descrição ≥ 10")
    rodape(ax, "RF02/RF03 — Abrir chamado e anexar arquivo · API: POST /api/chamados/ e POST /api/chamados/{id}/anexos/")
    return fig


def detalhe():
    fig, ax = tela("Tela 5 — Detalhe do chamado", "/chamados/{id}/", "chamados/detalhe.html", perfil="Técnico")
    ax.text(3, 13.5, "← Voltar para a lista", fontsize=8, color=ACC, va="center")
    card(ax, 3, 16, 62, 17)
    ax.text(5, 20, "#1 · Computador não liga", fontsize=11, fontweight="bold", color=INK, va="center"); badge(ax, 54, 18.8, "Em andamento", "#E65100")
    ax.text(5, 24, "Aberto por Ana Cliente em 20/11/2026 · Categoria: Hardware · Prioridade: Alta", fontsize=7.5, color=G4, va="center")
    ax.text(5, 28.5, "O computador da recepção não liga desde ontem à tarde.", fontsize=8.5, color=INK, va="center")
    ax.text(5, 31.5, "Anexos:  foto_roteador.jpg", fontsize=7.5, color=ACC, va="center")
    ax.text(3, 36, "Interações", fontsize=9.5, fontweight="bold", color=INK, va="center")
    card(ax, 3, 38, 62, 7); ax.text(4.5, 40.3, "Carlos Técnico · 21/11 14:20", fontsize=7, color=G4); ax.text(4.5, 43, "Vou verificar a fonte de alimentação ainda hoje.", fontsize=8, color=INK)
    ax.add_patch(FancyBboxPatch((3, 46.5), 62, 7, boxstyle="round,pad=0,rounding_size=.6", fc="#FFF8E1", ec="#F9A825", lw=1.1))
    ax.text(4.5, 48.8, "Carlos Técnico · 21/11 14:25 · nota interna", fontsize=7, color=G4); ax.text(4.5, 51.5, "Suspeita de fonte queimada. Verificar estoque.", fontsize=8, color=INK)
    card(ax, 3, 55, 62, 12); campo(ax, 5, 57.5, 58, "", h=4.5, valor="Novo comentário…"); ax.text(5, 64.5, "☐ Nota interna (invisível ao cliente)", fontsize=7.5, color=INK, va="center"); botao(ax, 51, 63, 12, "Comentar", h=2.8)
    card(ax, 68, 16, 29, 30, "Atendimento")
    ax.text(70, 22, "Técnico: Carlos Técnico", fontsize=8, color=INK)
    botao(ax, 70, 24, 25, "Assumir chamado", h=2.8)
    campo(ax, 70, 30, 25, "Alterar status", h=2.8, valor="Aguardando  ▾"); campo(ax, 70, 36, 25, "Prioridade", h=2.8, valor="Alta  ▾"); campo(ax, 70, 42, 25, "", h=2.2, valor="Atribuir (admin)  ▾")
    card(ax, 68, 48, 29, 19, "Histórico de status")
    for i, t in enumerate(["20/11 09:10  aberto", "21/11 10:02  aberto → em_andamento", "21/11 16:40  em_andamento → aguardando"]):
        ax.text(70, 54 + i * 3.6, t, fontsize=7.2, color=INK, va="center")
    rodape(ax, "RF05–RF08 — Comentar, assumir, alterar status/prioridade, atribuir · API: /api/chamados/{id}/(comentarios|assumir|status|atribuir)/")
    return fig


def dashboard():
    fig, ax = tela("Tela 6 — Dashboard de indicadores", "/dashboard/", "chamados/dashboard.html", perfil="Técnico")
    ax.text(3, 14.5, "Dashboard de chamados", fontsize=12, fontweight="bold", color=INK, va="center")
    for x, v, t in [(3, "8", "Chamados no total"), (51, "2", "Em aberto sem técnico")]:
        card(ax, x, 18, 46, 12); ax.text(x + 23, 23.5, v, fontsize=22, fontweight="bold", color=INK, ha="center", va="center"); ax.text(x + 23, 27.5, t, fontsize=8.5, color=G4, ha="center", va="center")
    for x, tit, itens in [(3, "Por status", [("Aberto", 2), ("Em andamento", 2), ("Aguardando cliente", 1), ("Resolvido", 0), ("Fechado", 3)]),
                          (51, "Por prioridade", [("Baixa", 2), ("Média", 2), ("Alta", 3), ("Crítica", 1)])]:
        card(ax, x, 33, 46, 31, tit)
        for i, (n, q) in enumerate(itens):
            y = 40 + i * 4.8
            ax.text(x + 2, y, n, fontsize=8.5, color=INK, va="center")
            ax.add_patch(Rectangle((x + 20, y - 1.1), max(q, 0.15) * 4.5, 2.2, fc=ACC if q else G3, ec="none"))
            ax.text(x + 22 + q * 4.5, y, str(q), fontsize=8, color=INK, va="center")
    rodape(ax, "RF10 — Indicadores (técnico/admin) · API: GET /api/dashboard/")
    return fig


if __name__ == "__main__":
    import os
    os.makedirs("wireframes", exist_ok=True)
    telas = [("01_login", login), ("02_cadastro", cadastro), ("03_lista_chamados", lista),
             ("04_novo_chamado", novo), ("05_detalhe_chamado", detalhe), ("06_dashboard", dashboard)]
    with PdfPages("wireframes/wireframes_helpdesk.pdf") as pdf:
        for nome, fn in telas:
            fig = fn()
            fig.savefig(f"wireframes/{nome}.png", dpi=130, bbox_inches="tight", facecolor="white")
            pdf.savefig(fig, bbox_inches="tight", facecolor="white")
            plt.close(fig)
    print("ok")
