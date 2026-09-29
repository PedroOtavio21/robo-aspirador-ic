> **DOCUMENTO GUIA IMUTÁVEL — NÃO ALTERAR.**
> Fonte de verdade do projeto. `PLANO.md`, `ARQUITETURA.md`, o código e a
> documentação final derivam deste arquivo. Qualquer alteração aqui invalida a
> entrega. Hash de integridade registrado no `README.md`.

---

Plano Estrutural do Entregável: Avaliação Experimental de Agentes Inteligentes

1. Introdução e Objetivos do Projeto

Finalidade: Compreender, projetar e avaliar o comportamento de agentes inteligentes em ambientes simulados.

Objetivos específicos:

Compreender os conceitos fundamentais de agentes inteligentes aplicados a diferentes tipos de ambientes de tarefas.

Projetar programas de agentes artificiais (reativo simples e reativo baseado em modelos), orientados por regras condição-ação.

Atuar em ambientes de tarefas determinísticos e parcialmente observáveis (como o problema clássico do aspirador de pó).

Avaliar empiricamente o desempenho e a racionalidade dos agentes desenvolvidos.

2. Justificativa e Fundamentação Teórica

Abordagem de Agentes: Entidades que interagem com o ambiente por meio de sensores e atuadores para alcançar objetivos específicos.

Contexto dos Sistemas Computacionais: A maioria dos sistemas artificiais atua em ambientes parcialmente observáveis.

Tipologias de Agentes a Desenvolver:

Agente Reativo Simples: Toma decisões baseando-se estritamente na percepção atual do ambiente, utilizando regras do tipo condição-ação.

Agente Baseado em Modelos: Mantém um estado interno para acompanhar aspectos do mundo que não são visíveis no momento (lidando com a observabilidade parcial), combinando-o com regras condição-ação.

Conceito de Racionalidade e Avaliação: A IA moderna define inteligência através da racionalidade. O projeto exige verificar se os agentes maximizam sua medida de desempenho de forma inteligente.

3. Metodologia e Especificações Técnicas

Ambiente de Simulação:

Domínio: Aspirador de pó.

Características: Determinístico e parcialmente observável.

Restrições de Informação: Os agentes desconhecem o padrão inicial de sujeira e a geografia do ambiente (extensão, limites e obstáculos). Os sensores operam de forma estritamente local.

Implementação dos Programas:

Desenvolvimento do agente reativo simples.

Desenvolvimento do agente baseado em modelos.

Medidas de Avaliação de Desempenho:

Critério 1: Premiação de $+1$ ponto para cada quadrado limpo em cada período.

Critério 2: Premiação de $+1$ ponto para cada quadrado limpo, penalizando com $-1$ ponto cada movimento realizado (eficiência de deslocamento).

Plano de Experimentação:

Fixar o tamanho do ambiente de teste.

Executar ambos os agentes em múltiplas configurações iniciais variando posições de sujeira, obstáculos e posições iniciais.

Registrar as pontuações individuais por configuração e calcular a pontuação média global de cada agente.

4. Estrutura da Apresentação Final (Até 10 Minutos)

Mecanismos Internos: Descrição detalhada da atualização de estado interno e da lógica de tomada de decisão de cada agente.

Análise Comportamental: Breve relato prático sobre como cada agente se comportou durante as simulações.

Resultados Empíricos: Apresentação de tabelas comparativas e gráficos consolidados com as pontuações obtidas.

Discussão Crítica: Análise profunda dos resultados sob a ótica da racionalidade de cada programa de agente implementado.
