# Controle de Coleta - FIIs (Fundamentus)

Este documento centraliza os dados que vamos extrair na primeira versão do bot de scraping.

## Fonte

- Site: `https://www.fundamentus.com.br/`
- Escopo inicial: tabela de FIIs

## Campos da Tabela

| Campo | Tipo esperado | Observação |
|------|---------------|-----------|
| Papel | string | Ticker do FII (ex.: `HGLG11`) |
| Segmento | string | Segmento do fundo |
| Cotação | decimal | Valor monetário, com normalização de vírgula/ponto |
| FFO Yield | decimal (%) | Percentual |
| P/VP | decimal | Múltiplo |
| Valor de Mercado | decimal | Valor monetário |
| Liquidez | decimal | Liquidez média/diária conforme fonte |
| Qtd de imoveis | inteiro | Quantidade de imóveis |
| Preço do m2 | decimal | Valor monetário por metro quadrado |
| Aluguel por m2 | decimal | Valor monetário por metro quadrado |
| Cap Rate | decimal (%) | Percentual |
| Vacância Média | decimal (%) | Percentual |

## Regras de Normalização (MVP)

- Remover espaços extras e caracteres invisíveis.
- Converter números em formato brasileiro (`1.234,56`) para decimal padrão (`1234.56`).
- Remover `%` dos campos percentuais e armazenar como número decimal.
- Preservar `Papel` em maiúsculo.
- Campos vazios devem virar `null`.

## Status Atual

- Concluído: mapeamento e extração da tabela geral.
- Concluído: extração de detalhes por ativo.
- Concluído: normalização dos campos.
- Concluído: snapshots JSON de execução.
- Concluído: persistência em PostgreSQL com upsert.

## Próximos Passos

- Implementar camada de serviço para consumo na API (queries para dashboard).
- Definir estratégia de agendamento do bot (cron/Celery).
- Criar métricas de qualidade da coleta (null-rate, tempo médio, falhas por ativo).
- Revisar nomenclatura de campos para padronização de domínio (pt/en).
- Preencher documentação de metodologia (`doc/03-Metodologia.md`).
