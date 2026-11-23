# Dicionário de dados — Help Desk

Banco relacional (PostgreSQL/SQLite). Estrutura criada por [`sql/01_ddl.sql`](../sql/01_ddl.sql) (equivalente às migrações do Django). Diagrama: [`etapa1/mer.png`](etapa1/mer.png).

## Relacionamentos

- departamento 1 — N usuario (um departamento tem vários usuários; usuário pode não ter departamento)
- departamento 1 — N categoria (cada categoria pertence a um departamento)
- categoria 1 — N chamado (todo chamado tem uma categoria)
- usuario 1 — N chamado, como solicitante (obrigatório)
- usuario 1 — N chamado, como técnico (opcional; nulo até o chamado ser assumido)
- chamado 1 — N comentario · chamado 1 — N anexo · chamado 1 — N historico_status (ao excluir o chamado, esses registros são excluídos junto)

## Tabelas

### `departamento`

Setores da organização responsáveis por atender categorias de chamados.

| Coluna | Tipo | Nulo? | Chave | Descrição |
|---|---|---|---|---|
| `id` | bigint | não | PK | Identificador único |
| `nome` | varchar(100) | não | único | Nome do departamento (único) |
| `descricao` | text | não |  | Descrição das responsabilidades |

### `usuario`

Pessoas que usam o sistema. O campo perfil define as permissões (cliente, técnico ou administrador).

| Coluna | Tipo | Nulo? | Chave | Descrição |
|---|---|---|---|---|
| `id` | bigint | não | PK | Identificador único |
| `last_login` | timestamptz | sim |  | Data/hora do último acesso |
| `nome` | varchar(150) | não |  | Nome completo |
| `email` | varchar(254) | não | único | E-mail usado no login (único) |
| `senha` | varchar(128) | não |  | Hash PBKDF2 da senha (nunca texto puro) |
| `perfil` | varchar(10) | não |  | cliente, tecnico ou admin |
| `ativo` | boolean | não |  | Se falso, o usuário não consegue entrar |
| `criado_em` | timestamptz | não |  | Data/hora do cadastro |
| `departamento_id` | bigint | sim | FK → departamento | Departamento do usuário (opcional) |

### `categoria`

Tipos de problema/solicitação; cada categoria pertence a um departamento.

| Coluna | Tipo | Nulo? | Chave | Descrição |
|---|---|---|---|---|
| `id` | bigint | não | PK | Identificador único |
| `nome` | varchar(100) | não |  | Nome da categoria (único dentro do departamento) |
| `descricao` | text | não |  | Descrição da categoria |
| `departamento_id` | bigint | não | FK → departamento | Departamento responsável |

### `chamado`

Registro central do sistema: solicitação de suporte aberta por um cliente.

| Coluna | Tipo | Nulo? | Chave | Descrição |
|---|---|---|---|---|
| `id` | bigint | não | PK | Identificador único (nº do chamado) |
| `titulo` | varchar(150) | não |  | Resumo do problema (mínimo 5 caracteres) |
| `descricao` | text | não |  | Detalhamento do problema (mínimo 10 caracteres) |
| `status` | varchar(15) | não |  | aberto, em_andamento, aguardando, resolvido ou fechado |
| `prioridade` | varchar(10) | não |  | baixa, media, alta ou critica |
| `solicitante_id` | bigint | não | FK → usuario | Usuário que abriu o chamado |
| `tecnico_id` | bigint | sim | FK → usuario | Técnico responsável (nulo até ser assumido) |
| `categoria_id` | bigint | não | FK → categoria | Categoria do chamado |
| `aberto_em` | timestamptz | não |  | Data/hora de abertura |
| `atualizado_em` | timestamptz | não |  | Data/hora da última alteração |
| `fechado_em` | timestamptz | sim |  | Data/hora do fechamento (nulo enquanto aberto) |

### `comentario`

Interações registradas no chamado. Notas internas só aparecem para a equipe.

| Coluna | Tipo | Nulo? | Chave | Descrição |
|---|---|---|---|---|
| `id` | bigint | não | PK | Identificador único |
| `chamado_id` | bigint | não | FK → chamado | Chamado comentado |
| `autor_id` | bigint | não | FK → usuario | Usuário autor |
| `texto` | text | não |  | Conteúdo do comentário |
| `interno` | boolean | não |  | Verdadeiro = nota visível só para técnico/admin |
| `criado_em` | timestamptz | não |  | Data/hora do comentário |

### `anexo`

Arquivos enviados no chamado (imagens, PDF, documentos até 5 MB).

| Coluna | Tipo | Nulo? | Chave | Descrição |
|---|---|---|---|---|
| `id` | bigint | não | PK | Identificador único |
| `chamado_id` | bigint | não | FK → chamado | Chamado do anexo |
| `enviado_por_id` | bigint | não | FK → usuario | Usuário que enviou |
| `arquivo` | varchar(255) | não |  | Caminho do arquivo em MEDIA_ROOT |
| `enviado_em` | timestamptz | não |  | Data/hora do envio |

### `historico_status`

Auditoria: cada mudança de status do chamado fica registrada.

| Coluna | Tipo | Nulo? | Chave | Descrição |
|---|---|---|---|---|
| `id` | bigint | não | PK | Identificador único |
| `chamado_id` | bigint | não | FK → chamado | Chamado afetado |
| `alterado_por_id` | bigint | não | FK → usuario | Usuário que alterou |
| `status_anterior` | varchar(15) | não |  | Status antes da mudança (vazio na abertura) |
| `status_novo` | varchar(15) | não |  | Status depois da mudança |
| `alterado_em` | timestamptz | não |  | Data/hora da mudança |

## Restrições de integridade

- `usuario.perfil` ∈ {cliente, tecnico, admin}; `usuario.email` único.
- `chamado.status` ∈ {aberto, em_andamento, aguardando, resolvido, fechado}; `chamado.prioridade` ∈ {baixa, media, alta, critica}.
- `chamado.fechado_em` nunca é anterior a `chamado.aberto_em`.
- `categoria` é única por departamento (`departamento_id`, `nome`).
- Exclusões: `RESTRICT` para dados de referência (categoria, solicitante, autor) e `CASCADE` para dependentes do chamado.
- Índices em `chamado.status`, `chamado.solicitante_id`, `chamado.tecnico_id` e `chamado.categoria_id` (filas e filtros).
