# Especificações do Projeto

## Introdução

Esta seção apresenta a especificação do projeto FinancialInsight sob a perspectiva das funcionalidades e comportamentos esperados do sistema, considerando as necessidades dos diferentes perfis de usuários envolvidos. O foco está na definição clara dos requisitos que permitirão a automatização da coleta, processamento e visualização de dados do mercado financeiro, especialmente no contexto de análise de Fundos Imobiliários (FIIs).

Para isso, são utilizadas técnicas de análise e especificação de requisitos que possibilitam estruturar as funcionalidades do sistema de forma objetiva, traduzindo as necessidades dos usuários em comportamentos mensuráveis e implementáveis. O objetivo é garantir que a solução seja eficiente, escalável e alinhada à proposta de simplificar o processo de análise de investimentos.

Nesta seção são apresentados os requisitos funcionais e não funcionais, as regras de negócio, as restrições e demais artefatos de especificação que definem o funcionamento do sistema. Esses elementos são fundamentais para orientar o desenvolvimento da aplicação, assegurar a consistência da solução proposta e garantir que o sistema atenda de forma adequada aos objetivos estabelecidos, proporcionando uma experiência clara, acessível e orientada a dados para o usuário final.

## Personas

## Personas

### 👤 João Silva, 32 anos — Investidor de Varejo (Iniciante/Intermediário)

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

### 📊 Mariana Costa, 28 anos — Usuária Analítica

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

### ⚙️ Carlos Mendes, 35 anos — Administrador do Sistema

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
| João Silva (Investidor de Varejo) | Investidor iniciante/intermediário | Visualizar um ranking dos melhores FIIs com base em indicadores | Identificar rapidamente boas oportunidades de investimento |
| João Silva (Investidor de Varejo) | Investidor iniciante/intermediário | Acessar dados organizados e simplificados | Reduzir a complexidade da análise financeira |
| João Silva (Investidor de Varejo) | Investidor iniciante/intermediário | Evitar análise manual de múltiplos ativos | Economizar tempo na tomada de decisão |
| Mariana Costa (Usuária Analítica) | Investidora orientada a dados | Definir filtros personalizados de análise | Aplicar sua própria estratégia de investimento |
| Mariana Costa (Usuária Analítica) | Investidora orientada a dados | Cadastrar preços-alvo para ativos | Identificar pontos ideais de entrada |
| Mariana Costa (Usuária Analítica) | Investidora orientada a dados | Receber alertas automáticos | Aproveitar oportunidades sem monitoramento constante |
| Carlos Mendes (Administrador) | Administrador do sistema | Monitorar a execução dos processos de scraping | Garantir a confiabilidade dos dados |
| Carlos Mendes (Administrador) | Administrador do sistema | Acompanhar métricas e logs da aplicação | Identificar falhas e manter a estabilidade do sistema |
| Carlos Mendes (Administrador) | Administrador do sistema | Atualizar seletores de coleta de dados | Manter o funcionamento do sistema diante de mudanças externas |