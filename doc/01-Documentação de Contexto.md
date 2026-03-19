# Documentação de Contexto: Projeto FinancialInsight

## Introdução

Nos últimos anos, a bolsa de valores brasileira, operada pela B3, registrou um crescimento expressivo no número de investidores pessoa física (CPFs), impulsionado principalmente pela redução das taxas de juros e pela busca por alternativas mais rentáveis em relação à renda fixa tradicional.

Além disso, observa-se uma crescente preocupação com a construção de renda passiva, especialmente por meio do recebimento de dividendos, estratégia amplamente difundida no mercado financeiro como forma de geração de fluxo de caixa recorrente para investidores de longo prazo.

Apesar da democratização do acesso às corretoras e plataformas digitais, a capacidade de análise de dados financeiros ainda representa uma barreira significativa para a maioria da população. Segundo estudos da ANBIMA, grande parte dos investidores brasileiros possui baixo nível de educação financeira, o que dificulta a tomada de decisões embasadas e aumenta a dependência de conteúdos genéricos ou recomendações pouco personalizadas.

Enquanto investidores institucionais contam com ferramentas avançadas de análise, como os terminais da Bloomberg L.P., que oferecem acesso a dados em tempo real, indicadores sofisticados e modelos analíticos robustos, o investidor de varejo geralmente depende de planilhas manuais, relatórios públicos ou plataformas com limitações analíticas.

Nesse contexto, este projeto propõe o desenvolvimento da **FinancialInsight**, uma plataforma web automatizada que atua como um “Radar de Oportunidades”, capaz de extrair dados públicos do mercado financeiro, aplicar modelos matemáticos de valuation e apresentar, de forma simplificada e visual, as melhores opções de investimento, reduzindo a complexidade analítica e ampliando o acesso à inteligência de mercado.

## Problema

Segundo dados da B3, milhões de brasileiros já investem em ativos de renda variável, como ações e Fundos Imobiliários (FIIs). No entanto, apesar do crescimento no número de investidores, a jornada de seleção de ativos ainda é complexa, técnica e exaustiva.

Atualmente, o investidor pessoa física precisa acessar múltiplos portais de dados financeiros, como o Fundamentus, extrair informações manualmente e lidar com planilhas extensas contendo centenas de ativos. Esse processo exige o cruzamento de diversos indicadores financeiros — como P/VP, Dividend Yield e Liquidez — o que demanda tempo, conhecimento técnico e organização.

Além disso, a ausência de ferramentas acessíveis que consolidem e interpretem esses dados de forma automatizada faz com que muitos investidores tomem decisões baseadas em informações incompletas ou superficiais, aumentando o risco de escolhas inadequadas.


## Objetivos

Desenvolver uma plataforma web completa (end-to-end) capaz de automatizar a extração de dados públicos do mercado financeiro, realizar o cruzamento inteligente de indicadores fundamentalistas e apresentar, de forma estruturada e visual, oportunidades de investimento para o investidor de varejo.

A solução terá como foco inicial os Fundos Imobiliários (FIIs), utilizando métricas como P/VP, Dividend Yield e Liquidez para gerar insights que aumentem a assertividade na tomada de decisão e reduzam significativamente o tempo necessário para análise manual.

## Justificativa

A educação financeira e o acesso à informação de qualidade são fatores essenciais para a redução das desigualdades econômicas e para a construção de patrimônio no longo prazo. No Brasil, estudos da ANBIMA indicam que grande parte da população ainda apresenta baixo nível de conhecimento financeiro, o que impacta diretamente a qualidade das decisões de investimento.

Paralelamente, o mercado financeiro é altamente dinâmico e orientado por dados, exigindo ferramentas capazes de acompanhar sua velocidade e complexidade. Nesse cenário, investidores que não possuem acesso a soluções analíticas acabam enfrentando desvantagens significativas na identificação de oportunidades.

Diante disso, o desenvolvimento do FinancialInsight se justifica por atuar diretamente na redução dessa assimetria de informação. A plataforma não apenas resolve uma dor técnica relacionada à coleta e análise de dados, mas também democratiza o acesso a metodologias de triagem que, tradicionalmente, são restritas a investidores institucionais ou profissionais do mercado.

Ao automatizar etapas críticas — como a coleta de dados e o cálculo de indicadores — o sistema assume o “trabalho pesado”, permitindo que o usuário concentre seus esforços na interpretação das informações e na tomada de decisão.

O impacto esperado do projeto é a ampliação do acesso a investimentos geradores de renda passiva, especialmente por meio de Fundos Imobiliários (FIIs), além da entrega de uma solução robusta, escalável e orientada a dados para o usuário final.

## Público-Alvo

O público-alvo da aplicação é composto por três perfis principais:

### Investidores de Varejo (Iniciantes e Intermediários)

Pessoas físicas que já possuem conta em corretoras e desejam construir uma carteira de investimentos voltada à geração de renda passiva, especialmente por meio de dividendos. Esse grupo enfrenta limitações de tempo e conhecimento técnico para realizar análises aprofundadas de múltiplos ativos, tornando-se o principal beneficiário da automação proposta pela plataforma.

---

### Usuários Analíticos

Investidores com perfil mais orientado a dados, que buscam maior controle sobre suas decisões de investimento. Esses usuários têm interesse em definir critérios personalizados — como preços-alvo e indicadores específicos — e receber alertas automatizados que auxiliem na otimização de seus aportes e estratégias.

---

### Administrador do Sistema

Responsável pela operação e sustentação da plataforma, incluindo o monitoramento da infraestrutura, manutenção dos seletores utilizados no processo de web scraping e acompanhamento de métricas e logs por meio de ferramentas de observabilidade, como o Grafana.

## Referências

- B3. Informações institucionais e estatísticas do mercado. Disponível em: <https://www.b3.com.br>. Acesso em: 2026.  
- ANBIMA. Raio X do Investidor Brasileiro. Disponível em: <https://www.anbima.com.br>. Acesso em: 2026.  
- Bloomberg. Bloomberg Terminal Overview. Disponível em: <https://www.bloomberg.com>. Acesso em: 2026.  
