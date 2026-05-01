# 03 - Metodologia

## Base operacional de atualizacao

Esta secao serve como base inicial da rotina de coleta e manutencao dos dados da aplicacao. A logica abaixo ainda e uma pseudologica de operacao e pode ser refinada quando houver implementacao de agendamento, monitoramento e novas fontes.

### Pseudologica
- Todo dia util as 18h: coletar cotacoes e multiplos.
- Toda segunda-feira: verificar se ha novos resultados trimestrais.
- Se detectar novo balanco: coletar os dados fundamentalistas da empresa afetada.
- Uma vez por mes: atualizar a lista de empresas para suportar configuracoes futuras e expansao da cobertura.

## Objetivo da rotina
- Manter no banco um snapshot suficientemente atual para consumo diario da aplicacao.
- Evitar execucao continua de scraping em tempo real.
- Separar atualizacao operacional do bot do consumo feito por API, dashboard e filtros.

## Observacoes
- A frequencia exata pode ser ajustada conforme custo, tempo de execucao e comportamento da fonte.
- O fluxo assume prioridade para dados atuais de consulta, sem exigir historico temporal completo nesta fase.
- A expansao para novas empresas, novos tipos de ativo ou novas fontes deve reaproveitar esta mesma logica como referencia inicial.
