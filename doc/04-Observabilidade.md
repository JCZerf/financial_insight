# 04 - Observabilidade

## Objetivo

Este documento centraliza a observabilidade do bot de coleta: metricas medidas, metricas derivadas, fontes de leitura e linha de base operacional observada em execucao completa.

## Fontes de observabilidade

- Log operacional: `data/logs/ingestor.log`
- Auditoria estruturada: `data/logs/extraction_audit.ndjson`
- Profiling de infraestrutura: `data/logs/docker_stats_YYYYMMDD_HHMMSS.csv`

## Metricas medidas diretamente

- `total_rows`: quantidade total de FIIs encontrados na tabela geral.
- `extraction_partial_seconds`: tempo de coleta da tabela geral.
- `extraction_complete_seconds`: tempo total da execucao do pipeline.
- `details_extraction_seconds`: tempo de coleta da etapa de detalhes.
- `duration_seconds` na persistencia geral e na persistencia de detalhes.
- `posted`, `updated`, `upserted` e `skipped` na escrita em banco.
- `collection_status` por ticker na etapa de detalhes.
- `concurrency`, `limit`, `headless` e `run_id` na auditoria da execucao.

## Metricas derivadas para leitura operacional

- Consultas logicas por execucao:
  - `1` consulta para a tabela geral.
  - `N` consultas de detalhe, sendo `N = total_rows` quando a execucao e completa com detalhes.
- Taxa de sucesso dos detalhes:
  - `detalhes com collection_status=success / total_rows`.
- Throughput geral:
  - `total_rows / extraction_complete_seconds`.
- Throughput da etapa de detalhes:
  - `total_rows / details_extraction_seconds`.
- Tempo medio amortizado da etapa de detalhes:
  - `details_extraction_seconds / total_rows`.
  - Observacao: essa metrica nao representa latencia individual real por request quando ha concorrencia; ela representa tempo medio amortizado da fase de detalhes.

## Linha de base observada

Execucao completa registrada em `2026-05-01`:

- `run_id`: `956c52e5-1b9a-4002-be76-882baaee80f6`
- `concurrency`: `4`
- `limit`: `null` (carga completa)
- `total_rows`: `557`
- Consultas logicas estimadas:
  - `1` consulta da tabela geral
  - `557` consultas de detalhe
  - `558` consultas logicas no total
- `extraction_partial_seconds`: `68.04s`
- `details_extraction_seconds`: `105.97s`
- `extraction_complete_seconds`: `174.02s`
- Throughput geral aproximado:
  - `3.20` FIIs/segundo
  - `192.04` FIIs/minuto
- Throughput da etapa de detalhes aproximado:
  - `5.26` detalhes/segundo
  - `315.37` detalhes/minuto
- Tempo medio amortizado da etapa de detalhes:
  - `0.19s` por FII
- Persistencia geral:
  - `0.08s`
  - `posted=5`
  - `updated=552`
  - `upserted=557`
- Persistencia de detalhes:
  - `0.11s`
  - `posted=5`
  - `updated=552`
  - `upserted=557`
  - `skipped=0`
- Taxa de sucesso dos detalhes observada:
  - `100%`

## Leitura pratica

- Se `extraction_complete_seconds` subir muito sem aumento relevante de `total_rows`, ha indicio de degradacao da fonte ou da execucao.
- Se `skipped` subir ou a taxa de sucesso cair, ha indicio de quebra na coleta de detalhes.
- Se `posted` subir de forma inesperada em massa, pode indicar mudanca na lista de tickers ou comportamento de upsert fora do padrao esperado.
- Se `docker_stats` mostrar CPU sustentada proxima do teto e memoria com pouca margem, a proxima degradacao mais provavel e de infraestrutura, nao de parser.
