# 05 - Modelo de Dados

## Escopo

Documentacao tecnica das tabelas de dominio persistidas pela aplicacao.

## Relacionamentos

```text
real_estate_fund (1) ----- (1) real_estate_fund_detail

real_estate_fund_detail.fund_id -> real_estate_fund.id
```

## Tabela `real_estate_fund`

**Descricao**

Armazena o snapshot atual dos dados gerais de cada FII extraidos da tabela principal do Fundamentus.

**Chaves e restricoes**

| Item | Definicao |
|---|---|
| Chave primaria | `id` |
| Chave unica | `ticker` |
| Indice | `idx_ref_ticker_collected (ticker, collected_at_utc)` |

**Campos**

| Campo | Tipo | Nulo | Chave/Indice | Descricao |
|---|---|---:|---|---|
| `id` | `bigint` | Nao | PK | Identificador interno do registro. |
| `run_id` | `uuid` | Nao | Indexado | Identificador da execucao de coleta que gravou o snapshot atual. |
| `source` | `varchar(120)` | Nao |  | Identificacao da fonte de dados. |
| `url` | `varchar(500)` | Nao |  | URL da origem da coleta da tabela geral. |
| `collected_at_utc` | `timestamp with time zone` | Nao | Indexado | Data e hora UTC da coleta. |
| `ticker` | `varchar(20)` | Nao | UNIQUE, Indexado | Codigo do FII. |
| `segment` | `varchar(120)` | Sim |  | Segmento do fundo. |
| `price` | `numeric(20,4)` | Sim |  | Cotacao do ativo. |
| `ffo_yield` | `numeric(10,4)` | Sim |  | FFO Yield. |
| `dividend_yield` | `numeric(10,4)` | Sim |  | Dividend Yield. |
| `price_to_book` | `numeric(12,4)` | Sim |  | Multiplo P/VP. |
| `market_value` | `numeric(24,2)` | Sim |  | Valor de mercado. |
| `liquidity` | `numeric(24,2)` | Sim |  | Liquidez informada na fonte. |
| `property_count` | `integer` | Sim |  | Quantidade de imoveis. |
| `price_per_sqm` | `numeric(20,4)` | Sim |  | Preco por metro quadrado. |
| `rent_per_sqm` | `numeric(20,4)` | Sim |  | Aluguel por metro quadrado. |
| `cap_rate` | `numeric(10,4)` | Sim |  | Cap rate. |
| `avg_vacancy` | `numeric(10,4)` | Sim |  | Vacancia media. |
| `created_at` | `timestamp with time zone` | Nao |  | Data de criacao do registro no banco. |
| `updated_at` | `timestamp with time zone` | Nao |  | Data da ultima atualizacao do registro no banco. |

## Tabela `real_estate_fund_detail`

**Descricao**

Armazena o snapshot atual dos dados detalhados de cada FII extraidos da pagina individual do ativo no Fundamentus.

**Chaves e restricoes**

| Item | Definicao |
|---|---|
| Chave primaria | `id` |
| Chave estrangeira | `fund_id -> real_estate_fund.id` |
| Cardinalidade | `1:1` com `real_estate_fund` |
| Restricao efetiva | `fund_id` unico por `OneToOneField` |
| Indice | `idx_ref_detail_run_status (run_id, collection_status)` |

**Campos**

| Campo | Tipo | Nulo | Chave/Indice | Descricao |
|---|---|---:|---|---|
| `id` | `bigint` | Nao | PK | Identificador interno do registro de detalhe. |
| `fund_id` | `bigint` | Nao | FK, UNIQUE | Referencia ao fundo em `real_estate_fund`. |
| `run_id` | `uuid` | Nao | Indexado | Identificador da execucao de coleta que gravou o detalhe atual. |
| `source` | `varchar(120)` | Nao |  | Identificacao da fonte de dados. |
| `url` | `varchar(500)` | Nao |  | URL da origem da coleta. |
| `detail_url` | `varchar(500)` | Sim |  | URL da pagina detalhada do ativo. |
| `collected_at_utc` | `timestamp with time zone` | Nao | Indexado | Data e hora UTC da coleta do detalhe. |
| `collection_status` | `varchar(32)` | Sim | Indice composto | Status da coleta do detalhe. |
| `identification_name` | `text` | Sim |  | Nome do fundo. |
| `identification_segment` | `varchar(120)` | Sim |  | Segmento do fundo na pagina detalhada. |
| `identification_mandate` | `varchar(120)` | Sim |  | Mandato do fundo. |
| `identification_management` | `varchar(120)` | Sim |  | Tipo de gestao. |
| `market_price` | `numeric(20,4)` | Sim |  | Cotacao na pagina de detalhe. |
| `market_last_quote_date` | `varchar(32)` | Sim |  | Data da ultima cotacao. |
| `market_low_52w` | `numeric(20,4)` | Sim |  | Minima em 52 semanas. |
| `market_high_52w` | `numeric(20,4)` | Sim |  | Maxima em 52 semanas. |
| `market_avg_volume_2m` | `numeric(24,2)` | Sim |  | Volume medio de 2 meses. |
| `market_market_value` | `numeric(24,2)` | Sim |  | Valor de mercado na pagina detalhada. |
| `market_share_count` | `numeric(24,2)` | Sim |  | Quantidade de cotas. |
| `market_report_date` | `varchar(32)` | Sim |  | Data do relatorio. |
| `market_last_quarter_info_date` | `varchar(32)` | Sim |  | Data da ultima informacao trimestral. |
| `oscillations` | `jsonb/json` | Sim |  | Bloco de oscilacoes do ativo, incluindo periodos e mapa anual. |
| `indicators_ffo_yield` | `numeric(10,4)` | Sim |  | FFO Yield detalhado. |
| `indicators_ffo_per_share` | `numeric(20,4)` | Sim |  | FFO por cota. |
| `indicators_dividend_yield` | `numeric(10,4)` | Sim |  | Dividend Yield detalhado. |
| `indicators_dividend_per_share` | `numeric(20,4)` | Sim |  | Dividendo por cota. |
| `indicators_price_to_book` | `numeric(12,4)` | Sim |  | Multiplo P/VP detalhado. |
| `indicators_book_value_per_share` | `numeric(20,4)` | Sim |  | Valor patrimonial por cota. |
| `results_last_12m_revenue` | `numeric(24,2)` | Sim |  | Receita dos ultimos 12 meses. |
| `results_last_3m_revenue` | `numeric(24,2)` | Sim |  | Receita dos ultimos 3 meses. |
| `results_last_12m_asset_sales` | `numeric(24,2)` | Sim |  | Venda de ativos nos ultimos 12 meses. |
| `results_last_3m_asset_sales` | `numeric(24,2)` | Sim |  | Venda de ativos nos ultimos 3 meses. |
| `results_last_12m_ffo` | `numeric(24,2)` | Sim |  | FFO dos ultimos 12 meses. |
| `results_last_3m_ffo` | `numeric(24,2)` | Sim |  | FFO dos ultimos 3 meses. |
| `results_last_12m_distributed_income` | `numeric(24,2)` | Sim |  | Resultado distribuido nos ultimos 12 meses. |
| `results_last_3m_distributed_income` | `numeric(24,2)` | Sim |  | Resultado distribuido nos ultimos 3 meses. |
| `balance_sheet_assets` | `numeric(24,2)` | Sim |  | Total de ativos. |
| `balance_sheet_net_equity` | `numeric(24,2)` | Sim |  | Patrimonio liquido. |
| `properties_property_count` | `integer` | Sim |  | Quantidade de propriedades. |
| `properties_unit_count` | `integer` | Sim |  | Quantidade de unidades. |
| `properties_area_sqm` | `numeric(24,4)` | Sim |  | Area total em metros quadrados. |
| `properties_price_per_sqm` | `numeric(24,4)` | Sim |  | Preco por metro quadrado. |
| `properties_rent_per_sqm` | `numeric(24,4)` | Sim |  | Aluguel por metro quadrado. |
| `properties_cap_rate` | `numeric(10,4)` | Sim |  | Cap rate detalhado. |
| `properties_avg_vacancy` | `numeric(10,4)` | Sim |  | Vacancia media detalhada. |
| `properties_to_equity_percent` | `numeric(10,4)` | Sim |  | Percentual de imoveis sobre patrimonio. |
| `created_at` | `timestamp with time zone` | Nao |  | Data de criacao do registro no banco. |
| `updated_at` | `timestamp with time zone` | Nao |  | Data da ultima atualizacao do registro no banco. |

## Politica de persistencia

| Tabela | Chave de upsert | Efeito |
|---|---|---|
| `real_estate_fund` | `ticker` | Mantem um unico registro atual por FII. |
| `real_estate_fund_detail` | `fund_id` | Mantem um unico registro detalhado atual por FII. |

## Tabelas de infraestrutura do Django

| Tabela | Finalidade |
|---|---|
| `django_migrations` | Controle de migracoes aplicadas. |
| `django_content_type` | Registro de content types do Django. |
| `auth_permission` | Permissoes do framework. |
| `auth_group` | Grupos de usuarios. |
| `auth_group_permissions` | Relacao entre grupos e permissoes. |
| `auth_user` | Usuarios do sistema. |
| `auth_user_groups` | Relacao entre usuarios e grupos. |
| `auth_user_user_permissions` | Relacao entre usuarios e permissoes. |
| `django_admin_log` | Log do admin Django. |
| `django_session` | Sessoes persistidas. |
