# Etapa 3 — Balanço do projeto: planejado × implementado

Revisão do planejamento da Etapa 1 (escopo, requisitos, tecnologias, arquitetura e diagramas) contra o que existe no repositório.

## 1. Requisitos funcionais

| Cód. | Requisito planejado | Situação | Onde está |
|---|---|---|---|
| RF01 | Autenticação com controle por perfil | ✅ Etapa 2 | `usuarios/`, telas de login/cadastro, `POST /api/auth/login/` |
| RF02 | Abrir chamado (título, descrição, categoria, prioridade) | ✅ Etapa 2 | `/chamados/novo/`, `POST /api/chamados/` |
| RF03 | Anexar arquivos | ✅ Etapa 2 | `services.anexar` (tipos e 5 MB validados) |
| RF04 | Listar/detalhar com filtros por status, prioridade e categoria | ✅ **completado na Etapa 3** (filtro por categoria só existia na API) | `chamado_lista`, `GET /api/chamados/` |
| RF05 | Comentários com nota interna | ✅ Etapa 2 | `services.comentar` |
| RF06 | Assumir e atribuir técnico | ✅ Etapa 2 | `assumir_chamado`, `atribuir_tecnico` |
| RF07 | Alterar status/prioridade com histórico | ✅ Etapa 2 | `alterar_status`, tabela `historico_status` |
| RF08 | Encerrar chamado | ✅ Etapa 2 | transição para `fechado` |
| RF09 | Cadastrar usuários, categorias e departamentos | ✅ **completado na Etapa 3** (categorias/departamentos só pelo Django Admin) | tela `/gerenciar/` + Admin |
| RF10 | Dashboard com indicadores e relatórios | ✅ **completado na Etapa 3** (faltavam gráficos, indicador por categoria e relatório) | `/dashboard/`, `/relatorios/chamados.csv` |

## 2. Itens planejados que estavam faltando (e foram implementados)

| Item | Origem no planejamento | Implementação |
|---|---|---|
| Gráficos no dashboard | Tecnologias: Chart.js | Rosca (status) e barras (prioridade, categoria); as tabelas continuam visíveis se o Chart.js não carregar |
| Indicador por categoria | Objetivo específico: "chamados por status, prioridade e categoria" | `services.indicadores()` e `GET /api/dashboard/` (`por_categoria`) |
| Relatório | RF10 "relatórios" | Exportação CSV (abre no Excel com acentos), restrita à equipe |
| Notificação | Diagrama de sequência "Abrir chamado" cobre a notificação | `services.notificar`: e-mail em novo chamado, mudança de status, assumir/atribuir e comentário público. Falha no envio nunca desfaz o chamado; nota interna nunca avisa o cliente |
| Filtro por categoria | RF04 | Lista de chamados |
| Gestão de categorias/departamentos | RF09 | Tela `/gerenciar/` com validação de nome e duplicidade |

## 3. Requisitos não funcionais

| Requisito | Situação |
|---|---|
| Senhas com hash | ✅ PBKDF2 do Django |
| Interface responsiva | ✅ Bootstrap 5 |
| Acesso restrito por perfil | ✅ regras em `services` + 404/403 |
| Git + documentação | ✅ README, dicionário de dados, exemplos de API, Postman |
| Testes automatizados (Django TestCase) | ✅ 47 testes passando |

## 4. Desvios em relação ao planejado (decisões conscientes)

- **App `relatorios`:** a Etapa 1 previa um app separado. O dashboard e o CSV ficaram no app `chamados`, que já concentra os dados e a camada de serviços; um app novo só duplicaria código.
- **Testes com pytest:** o plano citava "Django TestCase / pytest"; foi usado apenas o Django TestCase.
- **Fora do escopo (mantido):** SLA com alertas, integração WhatsApp/e-mail de entrada, app mobile e chat em tempo real continuam como evolução futura.

## 5. Plano de conclusão (Passo 4)

| Ação | Estado |
|---|---|
| Testes automatizados | ✅ 47 passando |
| Revisão da documentação | ✅ README e docs atualizados |
| Revisão final no navegador com os dados de demonstração | ⬜ a fazer antes da entrega |
| Preparar o pitch (roteiro e slides) | ⬜ próxima etapa |
| Conferir repositório (README, `.env.example`, professor como colaborador) | ⬜ antes da entrega |
