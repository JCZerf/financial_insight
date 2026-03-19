Documentação de Contexto: Projeto FinancialInsight
Introdução
Nos últimos anos, a bolsa de valores brasileira (B3) registrou um aumento histórico no número de investidores pessoa física (CPFs), impulsionado pela busca por rentabilidade superior à renda fixa tradicional e pela construção de renda passiva (dividendos). Apesar da democratização do acesso às corretoras, a inteligência e a análise de dados financeiros ainda são barreiras para a maioria da população.

Enquanto investidores institucionais possuem robôs e terminais caros (como a Bloomberg) para filtrar os melhores ativos, o investidor de varejo depende de análises manuais em planilhas ou de relatórios genéricos. Neste contexto, este projeto propõe o desenvolvimento da FinancialInsight, uma plataforma web automatizada que atua como um "Radar de Oportunidades", extraindo dados públicos do mercado, aplicando modelos matemáticos de valuation e entregando as melhores opções de investimento de forma mastigada e visual.

Problema
Segundo dados da B3, milhões de brasileiros investem atualmente em Ações e Fundos Imobiliários (FIIs). Contudo, a jornada de escolha dos ativos é complexa e exaustiva.

Atualmente, o investidor precisa acessar portais de dados financeiros (como o Fundamentus), exportar planilhas extensas com centenas de ativos e cruzar indicadores (como P/VP, Dividend Yield, Liquidez) manualmente.
As principais dores enfrentadas são:

Falta de tempo: Dificuldade em acompanhar as flutuações diárias de preços para encontrar o momento ideal de compra.

Excesso de informação (Sobrecarga): Plataformas gratuitas entregam todos os dados de uma vez, sem filtros inteligentes, causando paralisia por análise.

Atraso na tomada de decisão: O investidor perde oportunidades ("pechinchas") por não ter um sistema de alertas em tempo real quando um bom ativo atinge o preço desejado.

Objetivos
Objetivo geral:
Desenvolver uma plataforma web completa (Ponta a Ponta) que automatize a extração de dados do mercado financeiro, cruze indicadores de forma inteligente e conecte o investidor de varejo a oportunidades reais de investimento (focando inicialmente em Fundos Imobiliários), aumentando a assertividade e reduzindo o tempo de análise.

Objetivos específicos:

Desenvolver um Bot de RPA/Scraping autônomo para mapear e extrair indicadores diários de fontes públicas (Fundamentus).

Construir uma API RESTful (Django) estruturada para processar as regras de negócio e armazenar o histórico de cotações em banco de dados PostgreSQL.

Criar um Dashboard Web (Frontend) intuitivo para o usuário visualizar as "Pechinchas" (ativos baratos e pagadores de bons dividendos).

Implementar um sistema de Alertas e Notificações para avisar o usuário quando um ativo alvo atingir o preço desejado.

Estabelecer uma camada de Observabilidade (Grafana/Prometheus) para monitorar a saúde do robô e a taxa de sucesso das extrações.

Justificativa
A educação financeira e o acesso à informação de qualidade são fundamentais para a redução das desigualdades e para a construção de patrimônio a longo prazo. O mercado financeiro é dinâmico e exige ferramentas que acompanhem essa velocidade.

Ao criar o FinancialInsight, o projeto não apenas resolve uma dor técnica de análise de dados, mas democratiza o acesso a metodologias de triagem que antes eram restritas a profissionais. O sistema faz o "trabalho pesado" (coleta e matemática), permitindo que o usuário foque apenas na tomada de decisão.

O impacto esperado é a facilitação do acesso a investimentos geradores de renda passiva (FIIs), entregando uma ferramenta robusta, escalável e de alto valor agregado para o usuário final. Além disso, o projeto consolida uma arquitetura de software moderna (Scraping, APIs, React e DevOps), servindo como um case de engenharia de software de alto nível.

Público-Alvo
O público-alvo da aplicação é composto por:

Investidores de Varejo (Iniciantes e Intermediários): Pessoas físicas que já possuem conta em corretora e buscam construir uma carteira de dividendos, mas não têm tempo ou conhecimento avançado para analisar centenas de balanços financeiros.

Usuários Analíticos: Investidores que desejam cadastrar preços-alvo e receber notificações automatizadas para otimizar seus aportes mensais.

Administrador do Sistema: Responsável pelo monitoramento da infraestrutura, manutenção dos seletores do web scraper e análise das métricas no Grafana.
