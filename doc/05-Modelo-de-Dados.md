# 05 - Modelo de Dados

## Visao geral

Hoje a base do projeto esta organizada em dois grupos:

- Tabelas de dominio da aplicacao, que guardam os dados coletados dos FIIs.
- Tabelas de infraestrutura do Django, criadas automaticamente para suporte de admin, autenticacao, sessoes e migracoes.

O modelo atual esta orientado a **snapshot atual** dos ativos, e nao a historico completo. Em outras palavras: cada `ticker` representa o estado mais recente persistido para um FII.

## Diagrama simplificado

```text
real_estate_fund
  id (PK)
  ticker (UNIQUE)
  run_id
  source
  url
  collected_at_utc
  ...dados gerais...
        |
        | 1 : 1
        v
real_estate_fund_detail
  id (PK)
  fund_id (FK UNIQUE -> real_estate_fund.id)
  run_id
  source
  url
  detail_url
  collected_at_utc
  collection_status
  ...dados detalhados...
```

## Tabelas de dominio

### `real_estate_fund`

Tabela principal dos FIIs. Guarda os dados gerais extraidos da listagem do Fundamentus.

**Papel na arquitetura**
- Representa o cadastro operacional atual de cada FII.
- E a tabela-base para listagens, ranking, filtros e consultas rapidas.
- Usa `ticker` unico, entao cada ativo ocupa apenas uma linha no estado atual da base.

**Chaves e relacionamento**
- PK: `id`
- Chave natural operacional: `ticker`
- Relacionamento: `1:1` com `real_estate_fund_detail`

**Campos principais**
- Identificacao:
  - `id`
  - `ticker`
  - `segment`
- Metadados de coleta:
  - `run_id`
  - `source`
  - `url`
  - `collected_at_utc`
- Indicadores gerais:
  - `price`
  - `ffo_yield`
  - `dividend_yield`
  - `price_to_book`
  - `market_value`
  - `liquidity`
  - `property_count`
  - `price_per_sqm`
  - `rent_per_sqm`
  - `cap_rate`
  - `avg_vacancy`
- Auditoria de linha:
  - `created_at`
  - `updated_at`

**Indices e restricoes**
- `ticker` com `UNIQUE`
- indice composto:
  - `idx_ref_ticker_collected` em (`ticker`, `collected_at_utc`)

### `real_estate_fund_detail`

Tabela complementar que guarda os dados detalhados de cada FII, vindos da pagina individual do ativo.

**Papel na arquitetura**
- Enriquece o registro principal com dados mais profundos de mercado, resultados, balanco e propriedades.
- Existe uma linha de detalhe por fundo, acompanhando o mesmo conceito de snapshot atual.

**Chaves e relacionamento**
- PK: `id`
- FK unica: `fund_id -> real_estate_fund.id`
- Relacao `1:1`: um fundo tem no maximo um detalhe atual

**Campos principais**
- Metadados de coleta:
  - `run_id`
  - `source`
  - `url`
  - `detail_url`
  - `collected_at_utc`
  - `collection_status`
- Identificacao:
  - `identification_name`
  - `identification_segment`
  - `identification_mandate`
  - `identification_management`
- Mercado:
  - `market_price`
  - `market_last_quote_date`
  - `market_low_52w`
  - `market_high_52w`
  - `market_avg_volume_2m`
  - `market_market_value`
  - `market_share_count`
  - `market_report_date`
  - `market_last_quarter_info_date`
  - `oscillations` (`JSON`)
- Indicadores:
  - `indicators_ffo_yield`
  - `indicators_ffo_per_share`
  - `indicators_dividend_yield`
  - `indicators_dividend_per_share`
  - `indicators_price_to_book`
  - `indicators_book_value_per_share`
- Resultados:
  - `results_last_12m_revenue`
  - `results_last_3m_revenue`
  - `results_last_12m_asset_sales`
  - `results_last_3m_asset_sales`
  - `results_last_12m_ffo`
  - `results_last_3m_ffo`
  - `results_last_12m_distributed_income`
  - `results_last_3m_distributed_income`
- Balanco:
  - `balance_sheet_assets`
  - `balance_sheet_net_equity`
- Propriedades:
  - `properties_property_count`
  - `properties_unit_count`
  - `properties_area_sqm`
  - `properties_price_per_sqm`
  - `properties_rent_per_sqm`
  - `properties_cap_rate`
  - `properties_avg_vacancy`
  - `properties_to_equity_percent`
- Auditoria de linha:
  - `created_at`
  - `updated_at`

**Indices**
- `idx_ref_detail_run_status` em (`run_id`, `collection_status`)

## Relacao entre as tabelas

O fluxo logico do banco hoje e este:

1. O bot coleta a tabela geral.
2. Cada `ticker` e inserido ou atualizado em `real_estate_fund`.
3. Depois o bot coleta a pagina de detalhe de cada ativo.
4. O detalhe e associado ao fundo por `fund_id`.
5. O upsert de detalhes usa `fund_id` como chave de conflito, preservando apenas o estado mais recente daquele fundo.

## Como o upsert funciona hoje

### Tabela geral
- O conflito e resolvido por `ticker`.
- Se o `ticker` ja existe, os campos sao atualizados.
- Isso confirma que a tabela principal funciona como snapshot atual, nao historico por execucao.

### Tabela de detalhes
- O conflito e resolvido por `fund_id`.
- Se o fundo ja tem detalhe, o registro e atualizado.
- O detalhe sempre acompanha o ultimo estado conhecido do respectivo fundo.

## O que `run_id` representa

`run_id` identifica uma execucao especifica do bot. Ele ajuda em auditoria e rastreabilidade, mas **nao** define a chave principal do dado persistido atual.

Na pratica:
- varios fundos podem compartilhar o mesmo `run_id` em uma mesma rodada;
- uma nova execucao sobrescreve o snapshot anterior do mesmo `ticker`;
- o `run_id` atual serve para saber de qual coleta veio o estado salvo naquele momento.

## Campo `oscillations`

O campo `oscillations` fica em `real_estate_fund_detail` e usa `JSON`.

Ele foi modelado assim para suportar anos variaveis sem criar nova coluna a cada mudanca da fonte. O formato geral esperado e algo proximo de:

```json
{
  "day": -0.31,
  "month": 1.12,
  "days_30": 2.45,
  "months_12": 8.10,
  "year_to_date": 3.22,
  "yearly": {
    "2026": 3.22,
    "2025": 11.40
  }
}
```

## Tabelas automaticas do Django

Quando voce roda as migracoes, alem das tabelas de dominio, o Django tambem cria tabelas de infraestrutura. As principais sao:

- `django_migrations`
- `django_content_type`
- `auth_permission`
- `auth_group`
- `auth_group_permissions`
- `auth_user`
- `auth_user_groups`
- `auth_user_user_permissions`
- `django_admin_log`
- `django_session`

Essas tabelas nao pertencem ao dominio dos FIIs. Elas existem para:

- controle de migracoes;
- sistema de usuarios e permissoes;
- funcionamento do admin;
- gerenciamento de sessao.

## Leitura pratica

Se voce abrir o banco hoje, pense assim:

- `real_estate_fund`: lista principal de FIIs com dados resumidos.
- `real_estate_fund_detail`: complemento detalhado de cada FII.
- tabelas `django_*` e `auth_*`: infraestrutura do framework, nao dados do negocio.

## Limite atual do modelo

O desenho atual e bom para servir API de consulta atual, mas ainda nao e um modelo historico. Isso significa:

- voce consegue saber o estado mais recente do ativo;
- voce nao consegue, apenas com essas duas tabelas, comparar facilmente a evolucao de um ticker entre multiplas execucoes passadas;
- para historico temporal real, seria necessario introduzir tabelas de snapshot historico ou versionamento por coleta.
