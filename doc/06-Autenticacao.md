# 06 - Autenticacao

## Escopo

Documentacao tecnica do mecanismo de autenticacao da API, incluindo modelo de usuario, contrato dos endpoints, validacoes de entrada e ciclo de vida dos tokens JWT.

## Stack de autenticacao

| Componente | Funcao |
|---|---|
| `Django auth` | Base de autenticacao e hashing de senha |
| `accounts.User` | Modelo de usuario customizado |
| `Djoser` | Endpoints de cadastro e usuario autenticado |
| `SimpleJWT` | Emissao e renovacao de tokens JWT |
| `DRF JWTAuthentication` | Validacao do token Bearer nas rotas protegidas |

## Modelo de usuario

**Modelo:** `accounts.User`

| Campo | Tipo | Obrigatorio | Regra |
|---|---|---:|---|
| `email` | `email` | Sim | Identificador de login. Unico. Normalizado para lowercase. |
| `name` | `string` | Sim | Nome completo validado e normalizado. |
| `birth_date` | `date` | Sim | Data de nascimento valida, passada, idade entre 18 e 120 anos. |
| `cpf` | `string` | Sim | CPF validado, normalizado para 11 digitos e unico. |
| `password` | `string` | Sim | Senha validada por regras do Django e validacoes adicionais de identificacao pessoal. |
| `is_active` | `boolean` | Sim | Habilita autenticacao da conta. |
| `is_staff` | `boolean` | Sim | Habilita acesso ao admin Django. |
| `is_superuser` | `boolean` | Sim | Permissoes totais do Django. |
| `is_authorized` | `boolean` | Sim | Flag de autorizacao funcional da aplicacao. |

## Regras de validacao de cadastro

### `email`

- obrigatorio
- formato valido de email
- convertido para lowercase
- unico na base

### `name`

- obrigatorio
- espacos excedentes removidos
- minimo de 2 caracteres uteis
- minimo de 2 letras
- rejeita entradas sem conteudo alfabetico valido

### `birth_date`

- obrigatoria
- deve ser anterior a data atual
- idade minima: `18 anos`
- idade maxima aceita: `120 anos`

### `cpf`

- obrigatorio
- normalizado para apenas digitos
- deve conter exatamente `11` digitos
- rejeita sequencias repetidas
- valida digitos verificadores
- unico na base

### `password`

- obrigatoria
- validada pelos validadores padrao do Django
- nao pode conter dados de identificacao pessoal
- nao pode conter:
  - email completo
  - parte local do email
  - nome
  - nome sem espacos
  - CPF

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

## Politica de renovacao

| Regra | Comportamento |
|---|---|
| `ROTATE_REFRESH_TOKENS` | `True` |
| `BLACKLIST_AFTER_ROTATION` | `True` |
| `UPDATE_LAST_LOGIN` | `True` |

## Transporte do token

Todas as rotas protegidas devem receber o token no header HTTP:

```http
Authorization: Bearer <access_token>
```

## Endpoints de autenticacao

| Metodo | Rota | Autenticacao | Finalidade |
|---|---|---|---|
| `POST` | `/api/auth/users/` | Nao | Cadastro de usuario |
| `POST` | `/api/auth/jwt/create/` | Nao | Login com email e senha |
| `POST` | `/api/auth/jwt/refresh/` | Nao | Emissao de novo access token |
| `POST` | `/api/auth/jwt/verify/` | Nao | Verificacao de token |
| `GET` | `/api/auth/users/me/` | Sim | Dados do usuario autenticado |

## Contrato de cadastro

### Requisicao

```json
{
  "email": "ana@example.com",
  "name": "Ana Silva",
  "birth_date": "1995-08-12",
  "cpf": "12345678909",
  "password": "StrongPassword123!",
  "re_password": "StrongPassword123!"
}
```

### Resposta esperada

```json
{
  "id": 1,
  "email": "ana@example.com",
  "name": "Ana Silva",
  "birth_date": "1995-08-12",
  "cpf": "12345678909",
  "is_authorized": true
}
```

## Contrato de login

### Requisicao

```json
{
  "email": "ana@example.com",
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

## Contrato de usuario autenticado

### Requisicao

```http
GET /api/auth/users/me/
Authorization: Bearer <access_token>
```

### Resposta esperada

```json
{
  "id": 1,
  "email": "ana@example.com",
  "name": "Ana Silva",
  "birth_date": "1995-08-12",
  "cpf": "12345678909",
  "is_authorized": true
}
```

## Regras operacionais de uso no frontend

| Evento | Acao esperada |
|---|---|
| Login com sucesso | Persistir `access_token` e `refresh_token` conforme estrategia do frontend |
| Requisicao autenticada | Enviar `Authorization: Bearer <access_token>` |
| `401 Unauthorized` por expiracao de access token | Tentar `refresh` antes de redirecionar para login |
| Falha no refresh | Invalidar sessao local e exigir novo login |

## Regras de seguranca

- `access_token` de curta duracao
- `refresh_token` dedicado exclusivamente a renovacao de sessao
- rotacao de refresh token habilitada
- invalidacao de refresh token antigo apos renovacao
- hashing de senha realizado pelo Django
- tokens nao devem ser registrados em logs, URLs ou mensagens de erro
- HTTPS obrigatorio em ambiente de producao
