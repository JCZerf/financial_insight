# 99 - Decisões Técnicas

## 2026-03-21

### 1) Migrações Django enxutas (reset de histórico inicial)
- O app `api` foi consolidado para somente duas migrations:
  - `0001_initial`: cria schema já no estado final (nomes em inglês, tipos finais).
  - `0002_fund_upsert_key`: altera chave de upsert de `(run_id, ticker)` para `ticker` único.
- Foram removidas migrations intermediárias de rename/ajustes incrementais para evitar complexidade desnecessária no início do projeto.
- A base foi recriada limpa e as migrations aplicadas do zero com sucesso.

### 2) Padronização de nomenclatura em inglês no banco/modelos
- Campos de domínio passaram a ser definidos diretamente em inglês no schema inicial.
- Evitamos estratégia de "criar em PT-BR e renomear depois" para manter histórico simples e claro.

### 3) Playwright padronizado para arquitetura assíncrona
- `BrowserFactory` foi migrado para `playwright.async_api`.
- Operações de ciclo de vida do navegador (`start/new_page/close`) passaram a ser assíncronas.
- Context manager atualizado para `async with` (`__aenter__` / `__aexit__`).
- Tratamento de falha em inicialização com cleanup garantido (`close` em caso de erro).

### 4) Coerência de identidade de scraping
- A identidade de navegação passou a retornar perfil completo e consistente:
  - `user_agent`
  - `headers`
  - `locale`
  - `timezone_id`
  - `viewport`
- Objetivo: reduzir fingerprint inconsistente entre plataforma/headers/ambiente.
- Versões de UA foram alinhadas (macOS também em Chrome 122 para consistência com Windows).

### 5) Reuso de um único browser/context no pipeline
- O pipeline passou a reutilizar um único `BrowserFactory` para coleta geral + detalhes.
- Enquanto a tabela geral é lida, as coletas de detalhes já são agendadas em paralelo no mesmo contexto.
- Resultado esperado: menor overhead de bootstrap de browser e melhor eficiência de recursos em cloud.

### 6) Controle de consumo por configuração
- Foi definido limite de paralelismo de abas de detalhe via configuração:
  - env: `BOT_MAX_DETAIL_TABS`
  - CLI: `--concurrency` (override da env)
- Uso de `Semaphore` para controlar o máximo de abas simultâneas e proteger RAM/CPU.

### 7) Referer dinâmico para navegação mais realista
- Coleta da página geral envia `Referer: https://www.google.com.br/`.
- Coleta das páginas de detalhe envia `Referer: https://www.fundamentus.com.br/fii_resultado.php`.
- Objetivo: simular fluxo real de navegação lista -> detalhe.

### 8) Compatibilidade de execução local
- Imports com fallback mantidos para suportar execução:
  - como módulo (`python -m fundamentus_fii_ingestor.main`)
  - como script (`python fundamentus_fii_ingestor/main.py`)

### 9) Observação operacional
- O `docker-compose.yml` emite warning sobre `version` obsoleto. Não afeta execução atual, mas remover a chave é recomendado para evitar ruído.

### 10) Renomeação do serviço de scraping
- A pasta `bot/` foi renomeada para `fundamentus_fii_ingestor/` para explicitar o escopo funcional.
- Motivação: o projeto passará a ter múltiplos robôs/coletores (ex.: B3, Invest), e nomes genéricos aumentam ambiguidade.
- Impactos aplicados:
  - imports atualizados para `fundamentus_fii_ingestor.*`
  - comandos de execução/documentação atualizados
  - logger de auditoria renomeado para `fundamentus_fii_ingestor.audit`

### 11) Correção de concorrência no ciclo de vida do browser
- Foi identificado erro `TargetClosedError` ao coletar detalhes em paralelo.
- Causa raiz: tarefas de detalhe (`asyncio.gather`) eram aguardadas após sair do `async with BrowserFactory`, quando `context/browser` já estavam fechados.
- Correção: mover o `await asyncio.gather(*detail_tasks)` para dentro do bloco `async with`, garantindo recursos válidos até o fim das tarefas.
- Resultado: execução com `--limit 5 --detailed true` concluindo com sucesso (geral + detalhes).

### 12) Inclusão de Oscilações no baseline (sem migration incremental)
- O bloco de dados `Oscilações` foi incorporado ao schema inicial (`0001_initial`) em `RealEstateFundDetail`.
- Estratégia de modelagem: campo `oscillations` em `JSON` para suportar anos variáveis sem alterar schema a cada ano.
- Itens normalizados:
  - `day`, `month`, `days_30`, `months_12`
  - `year_to_date` (ano mais recente disponível)
  - `yearly` (mapa por ano, ex.: `{\"2026\": -5.06, ...}`)
- Persistência atualizada no upsert de detalhes (`db_persistence`).

### 13) Observabilidade de tempo de ponta a ponta da extração
- O pipeline passou a registrar tempos com foco operacional:
  - `Tempo de extracao parcial (dados gerais)`
  - `TEMPO TOTAL DE EXTRACAO (geral + detalhes)` (métrica principal)
  - `Tempo adicional de extracao de detalhes`
- A métrica de extração total foi ajustada para tempo real de relógio (início da coleta até término dos detalhes), evitando soma artificial de blocos.
- Os tempos também são enviados para auditoria em `raw_rows_collected`.

### 14) Métricas de persistência por tipo de operação (post/update)
- O upsert em `db_persistence` passou a retornar:
  - gerais: `upserted`, `posted`, `updated`
  - detalhes: `upserted`, `posted`, `updated`, `skipped`
- Implementação usa `RETURNING (xmax = 0) AS posted` para distinguir insert de update em lote.
- O pipeline agora loga duração e breakdown na persistência:
  - geral: tempo + `post/update/total`
  - detalhes: tempo + `post/update/total/skipped`

### 15) Ambiente de teste limitado via Docker (512MB / 1 CPU)
- Foi criado `Dockerfile.ingestor` para execução do bot em container dedicado.
- `docker-compose.yml` recebeu serviço `ingestor` com:
  - `mem_limit: 512m`
  - `cpus: 1.0`
- A base Playwright foi alinhada para `mcr.microsoft.com/playwright/python:v1.58.0-jammy` para compatibilidade com pacote Python instalado.
- A chave `version` foi removida do compose para eliminar warning de obsolescência.

### 16) Profiling de recursos para diagnosticar causa de falha
- Foi criado `scripts/profile_ingestor_resources.sh` para evitar diagnóstico por tentativa/erro.
- O script executa o ingestor, coleta `docker stats` por segundo e resume:
  - pico de CPU
  - pico de memória
  - `ExitCode`
  - `OOMKilled`
- Resultado observado nos testes:
  - `concurrency=2` em 512MB/1CPU opera no limite (CPU saturada e RAM muito próxima do teto).
  - `concurrency=1` aumenta estabilidade e completou o cenário de teste, mantendo CPU como gargalo principal.

### 17) PostgreSQL como camada de leitura da aplicação
- Foi definido que o bot de coleta nao sera executado sob demanda a cada consulta do usuario.
- O bot tera papel de ingestao periodica: atualizar o snapshot mais recente dos FIIs no banco.
- O PostgreSQL tera papel de camada de leitura da aplicacao, servindo API, dashboard e filtros sem necessidade de novo scraping a cada acesso.

**Motivacao**
- Executar scraping com Playwright em toda consulta tem custo maior de CPU, memoria e tempo de resposta.
- A leitura via banco e mais barata e previsivel do que abrir navegador e depender do HTML da fonte em tempo real.
- O desacoplamento entre coleta e consumo reduz dependencia operacional do Fundamentus durante o uso diario do sistema.
- Em caso de falha temporaria na coleta, a aplicacao continua podendo servir o ultimo snapshot valido persistido.

**Trade-off assumido**
- Ganha-se desempenho, previsibilidade e menor custo operacional por consulta.
- Em contrapartida, passa a existir custo fixo de manter o banco disponivel e aceita-se pequena defasagem entre a ultima coleta e o dado exibido.
- Para a fase atual do projeto, esse trade-off foi considerado favoravel porque o objetivo e evitar scraping continuo e preparar consumo recorrente via aplicacao.

**Implicacoes de arquitetura**
- O bot passa a ser um processo agendado, e nao um componente de resposta online.
- A API deve consultar prioritariamente o PostgreSQL, e nao acionar scraping em tempo real.
- O schema atual com `ticker` unico atende bem ao objetivo de manter o estado mais recente de cada FII.
- Historico temporal completo pode ser adicionado depois, caso o produto evolua para comparacao entre janelas ou alertas baseados em serie historica.
