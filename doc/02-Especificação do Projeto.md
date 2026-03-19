# Especificações do Projeto

## Introdução

Esta seção apresenta a especificação do projeto **FinancialInsight** sob a perspectiva das funcionalidades e comportamentos esperados do sistema, considerando as necessidades dos diferentes perfis de usuários envolvidos. O foco está na definição clara dos requisitos que permitirão a automatização da coleta, processamento e visualização de dados do mercado financeiro, especialmente no contexto de análise de Fundos Imobiliários (FIIs).

Para isso, são utilizadas técnicas de análise e especificação de requisitos que possibilitam estruturar as funcionalidades do sistema de forma objetiva, traduzindo as necessidades dos usuários em comportamentos mensuráveis e implementáveis. O objetivo é garantir que a solução seja eficiente, escalável e alinhada à proposta de simplificar o processo de análise de investimentos.

Nesta seção são apresentados os requisitos funcionais e não funcionais, as regras de negócio, as restrições e demais artefatos de especificação que definem o funcionamento do sistema. Esses elementos são fundamentais para orientar o desenvolvimento da aplicação, assegurar a consistência da solução proposta e garantir que o sistema atenda de forma adequada aos objetivos estabelecidos, proporcionando uma experiência clara, acessível e orientada a dados para o usuário final.

## Personas

### João Silva, 32 anos — Investidor de Varejo (Iniciante/Intermediário)

**Perfil:**  
João é analista administrativo e começou a investir recentemente buscando complementar sua renda no longo prazo. Possui conta em corretora e já investe em alguns Fundos Imobiliários, mas ainda não domina análise fundamentalista.

**Objetivo:**  
Construir uma carteira de renda passiva consistente por meio de FIIs, com boas oportunidades de entrada.

**Dores (Problemas):**  
- Falta de tempo para analisar múltiplos ativos  
- Dificuldade em interpretar indicadores financeiros  
- Dependência de conteúdos genéricos da internet  

**Necessidades:**  
- Visualizar rapidamente os melhores ativos disponíveis  
- Receber informações organizadas e confiáveis  
- Reduzir a complexidade da análise  

**Como o sistema ajuda:**  
- Apresenta ranking de ativos com base em indicadores (P/VP, Dividend Yield, Liquidez)  
- Automatiza a coleta e organização dos dados  
- Fornece uma interface simples e visual para tomada de decisão  

---

### Mariana Costa, 28 anos — Usuária Analítica

**Perfil:**  
Mariana é desenvolvedora e investidora com perfil mais técnico. Já possui conhecimento em indicadores fundamentalistas e busca otimizar suas decisões com base em dados.

**Objetivo:**  
Maximizar seus aportes mensais com base em critérios próprios, identificando oportunidades com maior precisão.

**Dores (Problemas):**  
- Perda de tempo validando dados manualmente  
- Falta de ferramentas acessíveis para automação de análise  
- Dificuldade em acompanhar preços ideais de entrada  

**Necessidades:**  
- Definir critérios personalizados de análise  
- Monitorar ativos com base em preços-alvo  
- Receber alertas automatizados  

**Como o sistema ajuda:**  
- Permite configuração de filtros personalizados  
- Possibilita cadastro de preços-alvo  
- Gera alertas automáticos quando condições são atendidas  

---

### Carlos Mendes, 35 anos — Administrador do Sistema

**Perfil:**  
Carlos é desenvolvedor responsável pela manutenção e evolução da plataforma. Atua no monitoramento da aplicação e na garantia da disponibilidade dos dados.

**Objetivo:**  
Assegurar o funcionamento contínuo do sistema, garantindo a confiabilidade dos dados e a estabilidade da aplicação.

**Dores (Problemas):**  
- Quebra de seletores devido a mudanças nas fontes de dados  
- Falhas em processos de scraping  
- Falta de visibilidade sobre o desempenho do sistema  

**Necessidades:**  
- Monitorar logs e métricas em tempo real  
- Identificar falhas rapidamente  
- Manter a integridade da coleta de dados  

**Como o sistema ajuda:**  
- Integra ferramentas de observabilidade (logs e métricas)  
- Permite monitoramento da infraestrutura e scraping  
- Facilita a manutenção e evolução contínua da plataforma  

## Histórias de Usuário

| Persona | Eu como... | Quero/Preciso... | Para... |
|--------|-----------|------------------|--------|
| João Silva | Investidor de varejo (iniciante/intermediário) | Visualizar um ranking dos melhores FIIs com base em indicadores | Identificar rapidamente boas oportunidades de investimento |
| João Silva | Investidor de varejo (iniciante/intermediário) | Acessar dados organizados e simplificados | Reduzir a complexidade da análise financeira |
| João Silva | Investidor de varejo (iniciante/intermediário) | Evitar análise manual de múltiplos ativos | Economizar tempo na tomada de decisão |
| Mariana Costa | Usuária analítica | Definir filtros personalizados de análise | Aplicar sua própria estratégia de investimento |
| Mariana Costa | Usuária analítica | Cadastrar preços-alvo para ativos | Identificar pontos ideais de entrada |
| Mariana Costa | Usuária analítica | Receber alertas automáticos | Aproveitar oportunidades sem monitoramento constante |
| Carlos Mendes | Administrador do sistema | Monitorar a execução dos processos de scraping | Garantir a confiabilidade dos dados |
| Carlos Mendes | Administrador do sistema | Acompanhar métricas e logs da aplicação | Identificar falhas e manter a estabilidade do sistema |
| Carlos Mendes | Administrador do sistema | Atualizar seletores de coleta de dados | Manter o funcionamento do sistema diante de mudanças externas |

# Modelagem do Processo de Negócio

## Análise da Situação Atual

Atualmente, investidores pessoa física realizam a análise de ativos de forma manual e descentralizada, utilizando múltiplas ferramentas como sites financeiros, planilhas eletrônicas e anotações próprias. Esse modelo apresenta diversas limitações que impactam diretamente a qualidade das decisões de investimento e a eficiência do processo analítico.

**Coleta de Dados:**  
Os usuários acessam diferentes plataformas para obter informações financeiras, como indicadores fundamentalistas, preços e histórico de ativos. Esse processo é fragmentado e exige navegação entre múltiplas fontes. Investidores como João (Analista Administrativo) perdem tempo consolidando dados que poderiam estar organizados em um único ambiente.

**Análise de Indicadores:**  
O cruzamento de métricas como P/VP, Dividend Yield e Liquidez é realizado manualmente em planilhas, exigindo conhecimento técnico e esforço operacional. Usuários com perfil iniciante ou intermediário enfrentam dificuldades para interpretar esses dados de forma consistente, o que pode levar a decisões pouco embasadas.

**Identificação de Oportunidades:**  
A descoberta de ativos atrativos depende de análises recorrentes e comparações constantes entre diferentes opções. Investidores como Mariana (Desenvolvedora) precisam repetir esse processo frequentemente, o que torna a atividade repetitiva e pouco escalável.

**Monitoramento de Preços:**  
O acompanhamento de preços e condições ideais de entrada é feito de forma manual, exigindo consultas frequentes ao mercado. A ausência de alertas automatizados faz com que oportunidades sejam perdidas, especialmente por usuários com rotina ocupada.

**Confiabilidade e Atualização de Dados:**  
A dependência de múltiplas fontes aumenta o risco de inconsistências e dados desatualizados. Além disso, não há garantia de padronização na forma como as informações são apresentadas, dificultando comparações diretas entre ativos.

Essa fragmentação de ferramentas, aliada à necessidade de esforço manual para coleta e análise de dados, cria barreiras significativas para que investidores consigam tomar decisões de forma ágil, segura e baseada em informações consistentes. Como resultado, muitos usuários enfrentam dificuldades para manter uma estratégia estruturada e identificar oportunidades de forma eficiente no mercado financeiro.

## Descrição Geral da Proposta

O FinancialInsight propõe uma solução integrada para análise de investimentos em renda variável, consolidando em uma única plataforma web as funcionalidades de coleta, processamento e visualização de dados do mercado financeiro. A proposta visa eliminar as barreiras identificadas na situação atual, oferecendo uma experiência simplificada, orientada a dados e acessível ao investidor de varejo.

A solução centraliza informações dispersas em diferentes fontes, automatiza o cruzamento de indicadores fundamentalistas e apresenta os resultados de forma estruturada e visual, permitindo que o usuário foque na tomada de decisão, e não no esforço operacional de análise.

---

### Escopo e Funcionalidades Principais

A aplicação permitirá que os usuários:

- Visualizem um ranking de ativos (FIIs) com base em indicadores como P/VP, Dividend Yield e Liquidez  
- Apliquem filtros personalizados para análise de ativos conforme sua estratégia  
- Acompanhem dados organizados e atualizados em uma interface centralizada  
- Cadastrem preços-alvo para ativos de interesse  
- Recebam alertas automatizados quando condições de mercado forem atendidas  
- Reduzam o tempo de análise por meio da automação do processo de coleta e cruzamento de dados  

---

### Alinhamento com Objetivos do Projeto

O FinancialInsight está alinhado com a proposta de democratização do acesso à informação financeira, reduzindo a assimetria de dados entre investidores institucionais e investidores de varejo. A solução atende à crescente demanda por ferramentas que apoiem decisões baseadas em dados, especialmente em um cenário de aumento da participação de pessoas físicas no mercado financeiro.

---

### Oportunidades de Melhoria

- **Redução de Esforço Operacional:** Eliminar a necessidade de coleta manual de dados em múltiplas fontes  
- **Centralização de Informações:** Consolidar indicadores financeiros em um único ambiente  
- **Apoio à Decisão:** Facilitar a identificação de oportunidades por meio de ranking e filtros  
- **Automação de Monitoramento:** Permitir acompanhamento contínuo do mercado com alertas automáticos  
- **Acessibilidade Analítica:** Tornar a análise de investimentos mais acessível a usuários com menor conhecimento técnico  

---

### Limites da Solução

- A plataforma não realiza recomendações financeiras personalizadas nem substitui assessoria de investimentos  
- Não executa ordens de compra ou venda, funcionando apenas como ferramenta de apoio à decisão  
- Depende da disponibilidade e consistência de dados provenientes de fontes públicas  
- A versão inicial terá foco em Fundos Imobiliários (FIIs), não contemplando outros tipos de ativos  
- A qualidade das análises está diretamente relacionada aos critérios definidos pelo usuário  

---

A proposta representa uma evolução em relação aos métodos tradicionais de análise manual, integrando automação, organização de dados e visualização inteligente para apoiar o investidor na tomada de decisões mais rápidas e fundamentadas.


## Processos do Sistema

### Processo 1 – ANÁLISE E IDENTIFICAÇÃO DE OPORTUNIDADES

Este processo representa o fluxo principal da aplicação, no qual o usuário acessa a plataforma para analisar ativos e identificar oportunidades de investimento com base em dados estruturados.

**Fluxo do Processo:**

**Início:** Usuário acessa a plataforma  
**Acessar Dashboard:** Sistema apresenta visão geral dos ativos disponíveis (FIIs)  

**Definir Critérios de Análise:**  
Usuário pode:
- Utilizar filtros padrão do sistema  
- Aplicar filtros personalizados (P/VP, Dividend Yield, Liquidez, etc.)

**Processamento:**  
Sistema realiza:
- Coleta de dados atualizados  
- Cruzamento de indicadores  
- Aplicação dos filtros definidos  

**Exibir Resultados:**  
Sistema apresenta ranking de ativos com base nos critérios selecionados  

**Decisão:** Usuário deseja analisar um ativo específico?  
- Se sim:  
  - Sistema exibe detalhes do ativo (indicadores, histórico, dados consolidados)  
- Se não:  
  - Permanece na listagem  

**Interação:**  
Usuário pode:
- Ajustar filtros  
- Ordenar resultados  

**Fim:** Usuário obtém insights para tomada de decisão  

---

**Oportunidades de Melhoria:**

- **Redução de Tempo de Análise:** Diminuir o tempo de análise de dezenas de minutos para poucos segundos  
- **Padronização de Dados:** Garantir consistência entre diferentes fontes  
- **Visualização Inteligente:** Apresentar dados de forma clara e comparável  
- **Apoio à Decisão:** Facilitar identificação de oportunidades com base em critérios objetivos  

---

### Processo 2 – MONITORAMENTO E ALERTAS DE OPORTUNIDADES

Este processo descreve como o usuário acompanha ativos de interesse e recebe notificações automáticas com base em condições previamente definidas.

**Fluxo do Processo:**

**Início:** Usuário acessa a área de monitoramento  

**Selecionar Ativo:**  
Usuário escolhe um ativo da lista ou busca manualmente  

**Definir Condições:**  
Usuário configura:
- Preço-alvo  
- Indicadores desejados (ex: P/VP abaixo de X, Dividend Yield acima de Y)  

**Salvar Monitoramento:**  
Sistema registra as condições definidas  

**Processamento Contínuo:**  
Sistema executa periodicamente:
- Atualização dos dados do mercado  
- Verificação das condições cadastradas  

**Decisão:** Condições foram atendidas?  
- Se não:  
  - Sistema continua monitoramento  
- Se sim:  
  - Gera alerta  

**Notificação:**  
Usuário recebe:
- Notificação na plataforma  
- (Opcional) alerta por e-mail  

**Ação do Usuário:**  
Usuário pode:
- Analisar o ativo  
- Ajustar condições  
- Remover monitoramento  

**Fim:** Usuário acompanha oportunidades de forma automatizada  

---

**Oportunidades de Melhoria:**

- **Automação de Monitoramento:** Eliminar necessidade de verificação manual constante  
- **Agilidade na Tomada de Decisão:** Notificar o usuário no momento ideal  
- **Personalização:** Permitir critérios específicos para diferentes estratégias  
- **Escalabilidade:** Monitorar múltiplos ativos simultaneamente  

## Indicadores de Desempenho

Para acompanhar a eficácia do FinancialInsight, foram definidos indicadores alinhados aos processos de análise de ativos e monitoramento de oportunidades. As métricas abaixo utilizam dados provenientes das interações do usuário com a plataforma, garantindo viabilidade de mensuração a partir dos registros de uso, filtros aplicados, ativos monitorados e alertas gerados.

| Indicador | Objetivo | Descrição | Cálculo | Fonte de Dados | Perspectiva |
|----------|----------|----------|--------|----------------|------------|
| Tempo médio de análise | Medir a eficiência na análise de ativos | Tempo médio que o usuário leva para aplicar filtros e visualizar resultados | Soma do tempo de análise / Nº de sessões de análise | Logs de navegação, eventos de filtro | Processos internos |
| Taxa de uso de filtros | Avaliar adoção de análise personalizada | Percentual de sessões em que filtros personalizados são utilizados | (Sessões com filtros / Total de sessões) × 100 | Logs de filtros aplicados | Produto |
| Taxa de visualização de ativos | Medir profundidade da análise | Percentual de usuários que acessam detalhes de ativos após visualizar o ranking | (Visualizações de ativos / Sessões com ranking) × 100 | Logs de navegação | Clientes |
| Taxa de ativos monitorados | Avaliar engajamento com monitoramento | Percentual de usuários que cadastraram ao menos um ativo para monitoramento | (Usuários com ativos monitorados / Usuários ativos) × 100 | Tabela de monitoramento de ativos, Tabela Usuário | Clientes |
| Taxa de disparo de alertas | Medir efetividade do sistema de monitoramento | Percentual de condições cadastradas que geraram alertas | (Alertas disparados / Condições cadastradas) × 100 | Tabela de alertas, Tabela de condições | Processos internos |
| Tempo de resposta do sistema | Avaliar desempenho da aplicação | Tempo médio de resposta para processamento e exibição de resultados | Soma do tempo de resposta / Nº de requisições | Logs da API | Processos internos |
| Retenção de usuários (30 dias) | Avaliar permanência dos usuários | Percentual de usuários que retornam à plataforma após 30 dias | (Usuários ativos após 30 dias / Usuários cadastrados) × 100 | Tabela Usuário, Logs de acesso | Crescimento |
| Frequência de uso da plataforma | Medir recorrência de uso | Média de acessos por usuário em um período (ex: semana) | Total de acessos / Nº de usuários ativos | Logs de acesso | Clientes |

## Requisitos

As tabelas a seguir apresentam os requisitos funcionais e não funcionais do projeto **FinancialInsight**, detalhando as capacidades esperadas da solução e os critérios de qualidade que deverão ser atendidos durante seu desenvolvimento.

Para definição da prioridade dos requisitos, foi adotada a técnica **MoSCoW** (*Must have, Should have, Could have, Won't have*), com o objetivo de organizar a implementação de acordo com a relevância de cada item para a proposta da versão inicial do sistema.

As categorias utilizadas são:

- **Must have:** requisitos essenciais para o funcionamento do sistema na versão inicial, sem os quais a solução não atende ao seu objetivo principal  
- **Should have:** requisitos importantes que agregam valor significativo à experiência do usuário, embora não sejam indispensáveis para a entrega do MVP  
- **Could have:** requisitos desejáveis, com potencial de ampliação funcional, mas que podem ser implementados em versões futuras  
- **Won't have:** requisitos explicitamente definidos como fora do escopo da versão atual  

A priorização dos requisitos considerou o tempo disponível para desenvolvimento, a capacidade de execução individual e a viabilidade técnica da implementação no contexto do projeto.

### Requisitos Funcionais

| ID | Descrição do Requisito | Prioridade | Persona Atendida |
|----|------------------------|-----------|------------------|
| RF-001 | O sistema deve permitir que o usuário visualize um ranking de ativos (FIIs) com base em indicadores financeiros | Must have | João, Mariana |
| RF-002 | O sistema deve permitir que o usuário aplique filtros personalizados (P/VP, Dividend Yield, Liquidez) na análise de ativos | Must have | João, Mariana |
| RF-003 | O sistema deve coletar, normalizar e consolidar automaticamente dados de fontes públicas do mercado financeiro | Must have | Todas |
| RF-004 | O sistema deve exibir informações detalhadas de um ativo selecionado, incluindo indicadores, histórico e dados consolidados | Must have | João, Mariana |
| RF-005 | O sistema deve permitir que o usuário cadastre ativos para monitoramento | Must have | Mariana |
| RF-006 | O sistema deve permitir que o usuário defina condições de monitoramento (ex: preço-alvo, indicadores) | Must have | Mariana |
| RF-007 | O sistema deve gerar alertas automáticos quando as condições de monitoramento forem atendidas | Must have | Mariana |
| RF-008 | O sistema deve permitir que o usuário visualize e gerencie seus ativos monitorados | Must have | Mariana |
| RF-009 | O sistema deve permitir ordenar e reorganizar os resultados da análise (ranking) | Should have | João |
| RF-010 | O sistema deve permitir salvar filtros personalizados para uso futuro | Could have | Mariana |
| RF-011 | O sistema deve permitir notificação de alertas via e-mail | Could have | Mariana |
| RF-012 | O sistema deve permitir que o administrador monitore o status dos processos de coleta de dados (scraping) | Must have | Carlos |
| RF-013 | O sistema deve permitir que o administrador visualize logs e métricas da aplicação | Must have | Carlos |
| RF-014 | O sistema deve permitir que o administrador atualize seletores utilizados na coleta de dados | Should have | Carlos |
| RF-015 | O sistema deve permitir autenticação de usuários e controle de sessão para associar preferências, monitoramentos e alertas a contas individuais | Must have | João, Mariana, Carlos |
| RF-016 | O sistema deve permitir atualização manual dos dados coletados em caso de falha no processo automático de coleta | Should have | Carlos |

### Requisitos Não Funcionais

| ID | Descrição do Requisito | Prioridade |
|----|------------------------|-----------|
| RNF-001 | O sistema deve apresentar tempo de resposta de até 3 segundos para carregamento das principais telas | Must have |
| RNF-002 | O sistema deve possuir interface web responsiva, permitindo uso em diferentes tamanhos de tela | Must have |
| RNF-003 | O sistema deve proteger credenciais e sessões de usuários autenticados por meio de mecanismos seguros de acesso | Must have |
| RNF-004 | O sistema deve registrar logs de execução, erros e eventos críticos para apoio à identificação de falhas | Must have |
| RNF-005 | O sistema deve permanecer disponível para consulta dos dados já armazenados mesmo diante de falhas pontuais no processo de coleta | Must have |
| RNF-006 | O código da aplicação deve ser organizado de forma modular, com separação clara entre frontend, backend e processo de coleta | Should have |
| RNF-007 | O sistema deve garantir rastreabilidade das coletas e dos alertas por meio de status, logs ou métricas operacionais | Should have |
| RNF-008 | O sistema deve armazenar os dados de forma persistente e consistente em banco de dados relacional | Must have |
| RNF-009 | O sistema deve tratar indisponibilidade temporária de fontes externas sem comprometer a integridade dos dados já armazenados | Should have |

### Restrições

O projeto está restrito pelos itens apresentados na tabela a seguir.

| ID | Restrição |
|----|----------|
| R-01 | O escopo do MVP deverá ser compatível com desenvolvimento incremental e entrega individual |
| R-02 | O sistema será desenvolvido como uma aplicação web, não contemplando versão mobile nesta etapa |
| R-03 | O projeto será desenvolvido e mantido inicialmente por uma única pessoa |
| R-04 | A coleta de dados dependerá de fontes públicas externas, podendo sofrer impacto por mudanças nessas fontes |
| R-05 | O sistema não realizará operações financeiras (compra/venda), atuando apenas como ferramenta de apoio à decisão |
| R-06 | O escopo inicial será limitado à análise de Fundos Imobiliários (FIIs) |
| R-07 | O sistema não oferecerá recomendações financeiras personalizadas |
