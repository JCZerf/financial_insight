# FinancialInsight

Plataforma para coleta, organização e visualização de dados do mercado financeiro, com foco inicial na análise de Fundos Imobiliários (FIIs) para apoiar decisões de investimento orientadas por dados.

## Visão Geral
- Coleta automatizada de dados públicos de fontes financeiras.
- Processamento, normalização e armazenamento de indicadores.
- API backend para expor dados e regras de negócio.
- Dashboard para visualização, análise e monitoramento de oportunidades.
- Estrutura pensada para apoiar filtros, ranking de ativos e alertas.

## Escopo Inicial
- Análise de FIIs com base em indicadores como P/VP, Dividend Yield e Liquidez.
- Identificação de oportunidades por meio de ranking e filtros.
- Monitoramento de ativos com condições definidas pelo usuário.
- Geração de alertas para apoiar o acompanhamento do mercado.

## Estado Atual
- Documentação de contexto e especificação já estruturadas.
- Projeto Django inicializado.
- Aplicação `api` criada para evolução do backend.
- Stack técnica definida com Python, Django, PostgreSQL e Playwright.
- Scraping, dashboard e observabilidade ainda em evolução.

## Stack Atual e Planejada
- Linguagem base: Python.
- Backend/API: Django.
- Banco de dados: PostgreSQL.
- Automação/Scraping: Playwright.
- Frontend/Dashboard: planejado.
- Observabilidade: planejada.

## Estrutura do Repositório
- `financial_insight/`: configuração principal do projeto Django.
- `api/`: aplicação backend para modelos, views e evolução da API.
- `doc/`: documentação do projeto.
- `manage.py`: ponto de entrada para comandos do Django.

## Documentação
- Contexto do projeto: `doc/01-Documentação de Contexto.md`.
- Especificação do projeto: `doc/02-Especificação do Projeto.md`.
- Metodologia: `doc/03-Metodologia.md`.

## Status
Projeto em fase inicial de estruturação, com documentação já consolidando escopo, requisitos e visão do produto para guiar o desenvolvimento incremental.
