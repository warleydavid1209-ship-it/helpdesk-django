# Exemplos práticos da API

Respostas **reais** obtidas ao executar o sistema com os dados de demonstração (`python manage.py carregar_demo`). Base: `http://127.0.0.1:8000/api`. Rotas protegidas exigem `Authorization: Token <token>` (obtido no login). A coleção do Postman está em [`postman_collection.json`](postman_collection.json).

Códigos HTTP usados: `200` ok · `201` criado · `400` dados inválidos/regra de negócio · `401` não autenticado · `403` sem permissão · `404` não encontrado.

## Cadastro — POST /api/auth/cadastro/ (201)

Requisição:

```bash
curl -X POST /api/auth/cadastro/ -H "Content-Type: application/json" -d '{"nome":"Maria Silva","email":"maria@exemplo.com","senha":"Senha@12345"}'
```

Resposta:

```json
{
  "id": 6,
  "nome": "Maria Silva",
  "email": "maria@exemplo.com",
  "perfil": "cliente",
  "perfil_display": "Cliente",
  "departamento": null,
  "criado_em": "2026-11-23T15:20:37.946822-03:00"
}
```

## Cadastro inválido (400)

Requisição:

```bash
curl -X POST /api/auth/cadastro/ -H "Content-Type: application/json" -d '{"nome":"Ma","email":"ana@cliente.com","senha":"123"}'
```

Resposta:

```json
{
  "nome": [
    "Informe o nome completo (mínimo 3 caracteres)."
  ],
  "email": [
    "usuario com este email já existe."
  ],
  "senha": [
    "Esta senha é muito curta. Ela precisa conter pelo menos 8 caracteres.",
    "Esta senha é muito comum.",
    "Esta senha é inteiramente numérica."
  ]
}
```

## Login (200)

Requisição:

```bash
curl -X POST /api/auth/login/ -H "Content-Type: application/json" -d '{"email":"ana@cliente.com","senha":"Senha@123"}'
```

Resposta:

```json
{
  "token": "<token>",
  "usuario": {
    "id": 4,
    "nome": "Ana Cliente",
    "email": "ana@cliente.com",
    "perfil": "cliente",
    "perfil_display": "Cliente",
    "departamento": 3,
    "criado_em": "2026-11-23T15:20:07.213822-03:00"
  }
}
```

## Login inválido (401)

Requisição:

```bash
curl -X POST /api/auth/login/ -H "Content-Type: application/json" -d '{"email":"ana@cliente.com","senha":"errada"}'
```

Resposta:

```json
{
  "detail": "E-mail ou senha inválidos."
}
```

## Abrir chamado (201)

Requisição:

```bash
curl -X POST /api/chamados/ -H "Authorization: Token <token>" -H "Content-Type: application/json" -d '{"titulo":"Monitor piscando","descricao":"O monitor pisca a cada poucos segundos.","categoria":1,"prioridade":"alta"}'
```

Resposta:

```json
{
  "id": 7,
  "titulo": "Monitor piscando",
  "descricao": "O monitor pisca a cada poucos segundos.",
  "status": "aberto",
  "status_display": "Aberto",
  "prioridade": "alta",
  "prioridade_display": "Alta",
  "solicitante": {
    "id": 4,
    "nome": "Ana Cliente"
  },
  "tecnico": null,
  "categoria": {
    "id": 1,
    "nome": "Hardware",
    "descricao": "",
    "departamento": 1,
    "departamento_nome": "Tecnologia da Informação"
  },
  "aberto_em": "2026-11-23T15:20:38.467365-03:00",
  "atualizado_em": "2026-11-23T15:20:38.467394-03:00",
  "fechado_em": null,
  "comentarios": [],
  "anexos": [],
  "historico": [
    {
      "id": 14,
      "status_anterior": "",
      "status_novo": "aberto",
      "alterado_por": {
        "id": 4,
        "nome": "Ana Cliente"
      },
      "alterado_em": "2026-11-23T15:20:38.468169-03:00"
    }
  ]
}
```

## Abrir chamado inválido (400)

Requisição:

```bash
curl -X POST /api/chamados/ -H "Authorization: Token <token>" -H "Content-Type: application/json" -d '{"titulo":"ab","descricao":"x","categoria":999}'
```

Resposta:

```json
{
  "titulo": [
    "O título deve ter pelo menos 5 caracteres."
  ],
  "descricao": [
    "A descrição deve ter pelo menos 10 caracteres."
  ],
  "categoria": [
    "Pk inválido \"999\" - objeto não existe."
  ]
}
```

## Sem token (401)

Requisição:

```bash
curl /api/chamados/
```

Resposta:

```json
{
  "detail": "As credenciais de autenticação não foram fornecidas."
}
```

## Cliente tenta assumir (403)

Requisição:

```bash
curl -X POST /api/chamados/2/assumir/ -H "Authorization: Token <token-do-cliente>"
```

Resposta:

```json
{
  "detail": "No Chamado matches the given query."
}
```

## Técnico assume (200)

Requisição:

```bash
curl -X POST /api/chamados/2/assumir/ -H "Authorization: Token <token-do-tecnico>"
```

Resposta:

```json
{
  "id": 2,
  "status": "em_andamento",
  "tecnico": {
    "id": 2,
    "nome": "Carlos Técnico"
  },
  "historico": [
    {
      "id": 3,
      "status_anterior": "",
      "status_novo": "aberto",
      "alterado_por": {
        "id": 5,
        "nome": "João Cliente"
      },
      "alterado_em": "2026-11-23T15:20:07.647359-03:00"
    },
    {
      "id": 15,
      "status_anterior": "aberto",
      "status_novo": "em_andamento",
      "alterado_por": {
        "id": 2,
        "nome": "Carlos Técnico"
      },
      "alterado_em": "2026-11-23T15:20:38.577208-03:00"
    }
  ]
}
```

## Transição inválida (400)

Requisição:

```bash
curl -X POST /api/chamados/2/status/ -H "Authorization: Token <token-do-tecnico>" -H "Content-Type: application/json" -d '{"status":"aberto"}'
```

Resposta:

```json
{
  "detail": "Transição não permitida: Em andamento → Aberto."
}
```

## Dashboard (200)

Requisição:

```bash
curl /api/dashboard/ -H "Authorization: Token <token-do-tecnico>"
```

Resposta:

```json
{
  "total": 7,
  "por_status": {
    "aberto": 2,
    "em_andamento": 2,
    "aguardando": 1,
    "resolvido": 1,
    "fechado": 1
  },
  "por_prioridade": {
    "baixa": 1,
    "media": 2,
    "alta": 3,
    "critica": 1
  },
  "por_categoria": {
    "Rede e Internet": 2,
    "Hardware": 2,
    "Software": 1,
    "Manutenção Predial": 1,
    "Climatização": 1
  },
  "sem_tecnico": 2
}
```

## Listar com filtro (200)

Requisição:

```bash
curl "/api/chamados/?status=em_andamento" -H "Authorization: Token <token-do-tecnico>"
```

Resposta:

```json
{
  "count": 2,
  "results": [
    {
      "id": 2,
      "titulo": "Instalar pacote Office",
      "status": "em_andamento",
      "prioridade": "media"
    },
    {
      "id": 1,
      "titulo": "Computador não liga",
      "status": "em_andamento",
      "prioridade": "alta"
    }
  ]
}
```
