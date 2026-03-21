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

## Próximos Passos

- Mapear seletores reais da tabela no Fundamentus.
- Implementar parser da linha HTML para este schema.
- Definir destino inicial dos dados (`JSON/CSV` ou banco de dados).
