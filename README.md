# FinancialInsight

Plataforma para coleta, normalização e persistência de dados de Fundos Imobiliários (FIIs), com foco em extração automatizada do Fundamentus.

## Stack
- Python
- Django
- PostgreSQL
- Playwright

## O Que Já Está Implementado
- Coleta da tabela geral de FIIs (`fii_resultado.php`).
- Coleta de detalhes por ativo (`detalhes.php?papel=...`) com concorrência controlada.
- Normalização de dados (números BR, percentuais e campos nulos).
- Logging operacional e auditoria de extração (`data/logs`).
- Medição de tempo da extração com destaque para tempo total:
  - `Tempo de extracao parcial (dados gerais)`
  - `TEMPO TOTAL DE EXTRACAO (geral + detalhes)`
  - `Tempo adicional de extracao de detalhes`
- Persistência em PostgreSQL com upsert (atualiza registros existentes por `papel`).
- Persistência com métrica de tempo e contagem por operação:
  - `post` (insert)
  - `update`
  - `total` e `skipped` (detalhes)
- Modelagem inicial com:
  - `RealEstateFund` (dados gerais)
  - `RealEstateFundDetail` (dados detalhados)

## Estrutura Principal
- `fundamentus_fii_ingestor/main.py`: entrada CLI do bot.
- `fundamentus_fii_ingestor/data_ingestor.py`: orquestração do pipeline.
- `fundamentus_fii_ingestor/fundamentus_extractor.py`: extração da tabela geral.
- `fundamentus_fii_ingestor/fundamentus_details_extractor.py`: extração de detalhes.
- `fundamentus_fii_ingestor/normalizers.py`: normalização de payload.
- `fundamentus_fii_ingestor/db_persistence.py`: upsert em lote no PostgreSQL.
- `api/models.py`: modelos Django.
- `doc/`: documentação funcional e de planejamento.

## Configuração Local
1. Instale dependências:
```bash
pip install -r requirements.txt
playwright install chromium
```

2. Configure ambiente:
```bash
cp .env.example .env
```

3. Suba PostgreSQL local com Docker:
```bash
docker compose up -d
```

4. Rode migrações:
```bash
python manage.py migrate
```

## Executando O Bot
Execução completa (geral + detalhes):
```bash
python3 fundamentus_fii_ingestor/main.py --detailed true --headless true
```

Teste com limite e concorrência reduzida:
```bash
python3 fundamentus_fii_ingestor/main.py --detailed true --limit 10 --concurrency 2 --headless true
```

Somente geral:
```bash
python3 fundamentus_fii_ingestor/main.py --detailed false --headless true
```

Somente detalhes:
```bash
python3 fundamentus_fii_ingestor/main.py --details-only --headless true
```

## Teste Em Ambiente Limitado (Docker)
Imagem do ingestor:
- `Dockerfile.ingestor` (base Playwright Python alinhada com a versão do pacote)

Serviço no compose:
- `ingestor` com limites:
  - `mem_limit: 512m`
  - `cpus: 1.0`

Comandos:
```bash
docker compose up -d postgres
docker compose build --no-cache ingestor
docker compose run --rm ingestor python3 fundamentus_fii_ingestor/main.py --detailed true --limit 50 --concurrency 1 --headless true
```

## Diagnóstico De CPU/RAM (Sem "Adivinhar")
Foi adicionado script de profiling para identificar causa de colapso:
- `scripts/profile_ingestor_resources.sh`

Ele:
- executa o ingestor em container dedicado;
- coleta `docker stats` por segundo (CPU, RAM, PIDs);
- resume `ExitCode` e `OOMKilled`;
- grava CSV em `data/logs/docker_stats_YYYYMMDD_HHMMSS.csv`.

Exemplo:
```bash
./scripts/profile_ingestor_resources.sh --detailed true --limit 50 --concurrency 2 --headless true
```

Leitura rápida:
- `OOMKilled: true` => falta de memória;
- CPU ~100% constante + `OOMKilled: false` => gargalo principal de CPU;
- memória próxima de 100% => operação com baixa margem de segurança.

## Saídas
- Snapshots:
  - `data/fii_general_snapshot.json`
  - `data/fii_details_snapshot.json`
- Logs:
  - `data/logs/ingestor.log`
  - `data/logs/extraction_audit.ndjson`

## Observabilidade
- Logs operacionais e de auditoria:
  - `data/logs/ingestor.log`
  - `data/logs/extraction_audit.ndjson`
- Profiling de infraestrutura:
  - `data/logs/docker_stats_YYYYMMDD_HHMMSS.csv`
- Metricas detalhadas, linha de base operacional e leitura dos sinais:
  - `doc/04-Observabilidade.md`

## Documentação
- Controle de coleta: `doc/00-Controle-Coleta-FIIs.md`
- Contexto: `doc/01-Documentação de Contexto.md`
- Especificação: `doc/02-Especificação do Projeto.md`
- Metodologia: `doc/03-Metodologia.md`
- Observabilidade: `doc/04-Observabilidade.md`
