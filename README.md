# Help Desk — Sistema de Gestão de Chamados

Projeto Integrador · **ADS — Uceff** · Aluno: **Warley David** · Professor: Caio Vinicio Koch dos Santos

Aplicação web em **Django** para abrir, atender e acompanhar chamados de suporte, com API REST, telas HTML e banco de dados relacional (SQLite para desenvolvimento e PostgreSQL).

| Etapa | Conteúdo | Onde está |
|---|---|---|
| 1 — Planejamento | Escopo, tecnologias, UML, MER, cronograma | [`docs/etapa1/`](docs/etapa1) |
| 2 — Funcionalidades básicas | Banco (DDL/DML), wireframes, API/back-end | este repositório |

---

## 1. Como executar

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # Windows: copy .env.example .env
python manage.py migrate
python manage.py carregar_demo    # dados de demonstração (opcional)
python manage.py runserver
```

Acesse **http://127.0.0.1:8000/** (telas) ou **http://127.0.0.1:8000/api/** (API).

Usuários de demonstração (senha de todos: `Senha@123`):

| Perfil | E-mail |
|---|---|
| Administrador | `admin@helpdesk.com` |
| Técnico | `carlos@helpdesk.com`, `marina@helpdesk.com` |
| Cliente | `ana@cliente.com`, `joao@cliente.com` |

---

## 2. Passo 1 — Banco de dados (DDL, DML e conexão)

Scripts SQL em [`sql/`](sql) (PostgreSQL 14+):

| Arquivo | Tipo | O que faz |
|---|---|---|
| `00_criar_banco.sql` | DDL | Cria o usuário e o banco `helpdesk`; documenta os ajustes para **conexão remota** |
| `01_ddl.sql` | **DDL** | Cria as 7 tabelas do MER, chaves, `CHECK`s e índices |
| `02_dml_dados_iniciais.sql` | **DML** | Carga inicial: departamentos, categorias, usuários, chamados, comentários, histórico |
| `03_dml_operacoes.sql` | **DML** | `INSERT`/`UPDATE`/`DELETE` e consultas (fila, indicadores, carga por técnico, tempo médio) |

```bash
psql -h localhost -U postgres -f sql/00_criar_banco.sql
psql -h localhost -U helpdesk_user -d helpdesk -f sql/01_ddl.sql
psql -h localhost -U helpdesk_user -d helpdesk -f sql/02_dml_dados_iniciais.sql
```

> Os scripts SQL e as migrações do Django (`python manage.py migrate`) geram **o mesmo esquema** (conferido coluna a coluna). Use um dos dois caminhos. Se criar o banco pelos scripts, rode depois `python manage.py migrate --fake-initial` para o Django criar apenas as tabelas auxiliares (sessões, tokens).

### Parâmetros de conexão (arquivo `.env`)

| Variável | Exemplo | Descrição |
|---|---|---|
| `DB_ENGINE` | `postgres` | `sqlite` (padrão) ou `postgres` |
| `DB_NAME` | `helpdesk` | Nome do banco |
| `DB_USER` / `DB_PASSWORD` | `helpdesk_user` / `helpdesk_pass` | Credenciais |
| `DB_HOST` | `localhost` ou IP/domínio do servidor | Host (local ou remoto) |
| `DB_PORT` | `5432` | Porta |
| `DB_SSLMODE` | `prefer` / `require` | Use `require` em conexões remotas |

**Conexão remota:** no servidor PostgreSQL, ajuste `listen_addresses` (`postgresql.conf`), libere o IP em `pg_hba.conf` com `hostssl ... scram-sha-256` e abra a porta 5432 no firewall. Detalhes comentados em `sql/00_criar_banco.sql`. Para subir um PostgreSQL local rapidamente: `docker compose up -d`.

### Modelo de dados

Tabelas: `departamento`, `usuario`, `categoria`, `chamado`, `comentario`, `anexo`, `historico_status` (diagrama MER em [`docs/etapa1/mer.png`](docs/etapa1/mer.png)).

---

## 3. Passo 2 — Telas e wireframes

Wireframes em [`docs/wireframes/`](docs/wireframes) (PNG e [PDF único](docs/wireframes/wireframes_helpdesk.pdf)), gerados por `docs/gerar_wireframes.py`. Cada wireframe corresponde a uma tela implementada:

| Wireframe | Tela | Rota | Template | View |
|---|---|---|---|---|
| `01_login.png` | Login | `/login/` | `templates/usuarios/login.html` | `auth_views.LoginView` |
| `02_cadastro.png` | Cadastro de cliente | `/cadastro/` | `templates/usuarios/cadastro.html` | `chamados/web.py::cadastro` |
| `03_lista_chamados.png` | Lista / fila de chamados | `/` | `templates/chamados/lista.html` | `chamados/web.py::chamado_lista` |
| `04_novo_chamado.png` | Abrir chamado | `/chamados/novo/` | `templates/chamados/novo.html` | `chamados/web.py::chamado_novo` |
| `05_detalhe_chamado.png` | Detalhe do chamado | `/chamados/<id>/` | `templates/chamados/detalhe.html` | `chamados/web.py::chamado_detalhe` |
| `06_dashboard.png` | Dashboard | `/dashboard/` | `templates/chamados/dashboard.html` | `chamados/web.py::dashboard` |

---

## 4. Passo 3 — API / back-end

Todas as operações passam pelas regras de negócio de [`chamados/services.py`](chamados/services.py), usadas tanto pela API quanto pelas telas. O fluxo de cada requisição segue os quatro pontos pedidos na atividade:

1. **Recebimento** — requisição HTTP (Postman/cURL) ou formulário de tela;
2. **Validação/tratamento** — serializers do DRF e regras de negócio (tamanhos mínimos, transições de status, permissões por perfil, tipo/tamanho de anexo);
3. **Persistência/consulta** — ORM do Django (PostgreSQL ou SQLite), com transações e histórico de status;
4. **Retorno** — JSON com o recurso criado/atualizado e códigos HTTP coerentes (`200`, `201`, `400`, `401`, `403`, `404`).

Autenticação por **token**: envie `Authorization: Token <token>`.

| Método e rota | Perfil | Descrição |
|---|---|---|
| `POST /api/auth/cadastro/` | público | Cria usuário **cliente** |
| `POST /api/auth/login/` | público | Retorna `token` |
| `POST /api/auth/logout/` · `GET /api/auth/me/` | logado | Encerra sessão / dados do usuário |
| `GET /api/categorias/` · `GET /api/departamentos/` | logado | Listas auxiliares |
| `GET /api/usuarios/?perfil=tecnico` | equipe | Lista usuários |
| `GET /api/chamados/` | logado | Lista (cliente: só os seus). Filtros: `status`, `prioridade`, `categoria`, `q`, `sem_tecnico=1`, `meus=1` |
| `POST /api/chamados/` | logado | Abre chamado |
| `GET /api/chamados/<id>/` | dono ou equipe | Detalhe, comentários, anexos e histórico |
| `PATCH /api/chamados/<id>/` | equipe | Altera a prioridade |
| `POST /api/chamados/<id>/status/` | equipe | Altera o status (valida transições) |
| `POST /api/chamados/<id>/assumir/` | equipe | Assume o chamado |
| `POST /api/chamados/<id>/atribuir/` | admin | Atribui técnico |
| `GET/POST /api/chamados/<id>/comentarios/` | dono ou equipe | Comentários (`interno` só equipe) |
| `POST /api/chamados/<id>/anexos/` | dono ou equipe | Upload (`multipart`, até 5 MB) |
| `GET /api/dashboard/` | equipe | Indicadores |

Exemplo:

```bash
# login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"email":"ana@cliente.com","senha":"Senha@123"}'

# abrir chamado
curl -X POST http://127.0.0.1:8000/api/chamados/ \
     -H "Authorization: Token <token>" -H "Content-Type: application/json" \
     -d '{"titulo":"Monitor piscando","descricao":"O monitor pisca a cada poucos segundos.","categoria":1,"prioridade":"alta"}'
```

Coleção do **Postman** pronta: [`docs/postman_collection.json`](docs/postman_collection.json) (importe, rode *Login* e use as demais requisições).

**Status e transições:** `aberto → em_andamento → aguardando ⇄ em_andamento → resolvido → fechado` (chamado `fechado` não aceita comentários, anexos nem novas transições).

---

## 5. Testes

```bash
python manage.py test
```

36 testes automatizados (autenticação, validação de payload, permissões por perfil, fluxo de status, notas internas, anexos, dashboard e telas). Executados com sucesso em **SQLite** e **PostgreSQL 16**.

## 6. Estrutura

```
config/        configurações e rotas
usuarios/      usuário (perfis), departamento, cadastro/login (API)
chamados/      models, services (regras), API (views/serializers), telas (web.py), testes
templates/     telas HTML (Bootstrap 5)
sql/           scripts DDL e DML (PostgreSQL)
docs/          etapa 1, wireframes, coleção Postman
```

## 7. Próximas etapas
Refinar a interface, e-mails de notificação, SLA com prazos, relatórios exportáveis e publicação (deploy).
