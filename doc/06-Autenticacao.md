# 06 - Autenticacao

## Objetivo

Documentar o fluxo de autenticacao da API, o ciclo de vida dos tokens e o contrato esperado entre frontend e backend.

## Fluxo de autenticacao

```text
1. Usuario envia email + senha
   POST /api/auth/jwt/create/

2. API retorna:
   - access_token
   - refresh_token

3. Frontend envia o access_token em cada requisicao protegida
   Authorization: Bearer <access_token>

4. Quando o access_token expira, o frontend usa o refresh_token
   POST /api/auth/jwt/refresh/

5. API retorna novo access_token
   sem exigir novo login
```

## Politica de tokens

| Token | Finalidade | Validade |
|---|---|---|
| `access_token` | Autorizar acesso as rotas protegidas da API | `15 minutos` |
| `refresh_token` | Obter novo `access_token` sem novo login | `7 dias` |

## Transporte do token

Todas as rotas protegidas devem receber o token no header HTTP:

```http
Authorization: Bearer <access_token>
```

## Endpoints de autenticacao

| Metodo | Rota | Finalidade |
|---|---|---|
| `POST` | `/api/auth/users/` | Cadastro de usuario |
| `POST` | `/api/auth/jwt/create/` | Login com email e senha |
| `POST` | `/api/auth/jwt/refresh/` | Emissao de novo access token |
| `POST` | `/api/auth/jwt/verify/` | Verificacao de token |
| `GET` | `/api/auth/users/me/` | Dados do usuario autenticado |

## Contrato de login

### Requisicao

```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!"
}
```

### Resposta esperada

```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

## Contrato de refresh

### Requisicao

```json
{
  "refresh": "<refresh_token>"
}
```

### Resposta esperada

```json
{
  "access": "<new_access_token>"
}
```

## Comportamento esperado no frontend

| Evento | Acao esperada |
|---|---|
| Login com sucesso | Persistir `access_token` e `refresh_token` conforme estrategia do frontend |
| Requisicao autenticada | Enviar `Authorization: Bearer <access_token>` |
| `401 Unauthorized` por expiracao de access token | Tentar `refresh` antes de redirecionar para login |
| Falha no refresh | Invalidar sessao local e exigir novo login |

## Observacoes de seguranca

- O `access_token` deve ser de curta duracao.
- O `refresh_token` deve ser usado apenas para renovacao de sessao.
- A API deve operar com HTTPS em ambiente de producao.
- Tokens nao devem ser expostos em logs, URLs ou mensagens de erro.
- O backend esta configurado para rotacionar refresh tokens e invalidar tokens antigos apos renovacao.
