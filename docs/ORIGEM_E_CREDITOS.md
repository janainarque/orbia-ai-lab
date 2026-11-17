# Origem, créditos e evidências

## 1. Sobre o Orbia Intelligence

O Orbia Intelligence é um laboratório independente de análise de dados, estatísticas descritivas, modelagem matemática e simulação experimental aplicada ao futebol.

O projeto foi desenvolvido de maneira incremental, incorporando ferramentas de engenharia de dados, validação, visualização interativa, testes automatizados e avaliação experimental de força relativa de seleções.

O repositório possui implementação própria e mantém documentadas as referências externas utilizadas.

## 2. Origem do estudo de caso

O estudo inicial foi motivado por uma demonstração do projeto [IAPredict — Copa 2026](https://github.com/marcovsilva/iapredict-copa2026), de Marcos Vinicius da Silva.

A demonstração apresentou probabilidades relacionadas a seleções participantes da Copa do Mundo de 2026.

O Orbia utilizou quatro valores observados nesse material como ponto de partida para um estudo independente de visualização e análise descritiva.

| Seleção | Probabilidade observada |
|---|---:|
| Espanha | 16,9% |
| Argentina | 16,4% |
| França | 8,0% |
| Brasil | 6,4% |

Esses valores totalizam 47,7%. Os demais 52,3% da distribuição não estão individualmente disponíveis no material utilizado.

Os percentuais não foram produzidos pelo Orbia e não devem ser interpretados como previsões próprias ou como uma distribuição probabilística completa.

A observação desses valores não comprova a calibração, a precisão ou a capacidade preditiva do projeto de origem.

## 3. Independência da implementação

O Orbia Intelligence não é uma reprodução do IAPredict.

A implementação do Orbia foi desenvolvida independentemente e possui seus próprios componentes de:

- Validação e processamento de dados.
- Estatísticas descritivas de partidas internacionais.
- Ranking histórico por aproveitamento.
- Simulação experimental Monte Carlo.
- Motor experimental de rating Elo.
- Ranking de força relativa.
- Evolução histórica dos ratings.
- Visualização interativa com Streamlit e Altair.
- Testes automatizados.

Não foi incorporado código do pipeline original do IAPredict.

As referências ao projeto de origem são mantidas para reconhecer a inspiração do estudo de caso, sem atribuir ao Orbia resultados ou funcionalidades desenvolvidos por terceiros.

## 4. Fonte dos dados históricos

A infraestrutura histórica utiliza dados provenientes do repositório público:

[International Football Results — martj42](https://github.com/martj42/international_results)

A fonte declara a licença CC0 1.0.

Para permitir rastreabilidade e reprodução, o Orbia mantém um snapshot versionado da base original, com identificação de commit e verificação de integridade por SHA-256.

O processamento realizado identificou:

- 49.940 registros originais.
- 49.938 partidas aprovadas.
- Dois registros conflitantes preservados em quarentena.

Os registros conflitantes não foram corrigidos mediante escolha arbitrária de um dos placares.

A base processada pode ser reconstruída a partir do snapshot armazenado no projeto.

A procedência, os critérios de validação e as limitações estão documentados em [DADOS_FUTEBOL.md](DADOS_FUTEBOL.md).

## 5. Metodologia Elo desenvolvida no Orbia

A V7 introduziu um motor experimental de avaliação de força relativa baseado nos resultados históricos disponíveis.

A implementação utiliza:

- Rating inicial de 1500 pontos.
- Fator K fixo de 20 pontos.
- Cálculo do resultado esperado de cada confronto.
- Atualização dos ratings após vitórias, empates e derrotas.
- Processamento cronológico das partidas por data.
- Ordenação determinística para partidas na mesma data.
- Cálculo de rankings em datas históricas.
- Filtros por quantidade mínima de partidas e atividade recente.
- Evolução anual dos ratings.

O modelo não aplica, nesta versão, vantagem de mando, ponderação por competição ou ajuste pela diferença de gols.

O Elo é uma metodologia matemática conhecida. A contribuição do Orbia consiste na implementação, integração com a infraestrutura histórica, definição dos parâmetros experimentais, construção das visualizações e testes.

Os ratings calculados não correspondem ao ranking oficial da FIFA e sua capacidade preditiva ainda não foi validada.

## 6. Simulação Monte Carlo

O Orbia também possui um simulador experimental de torneio eliminatório com quatro seleções.

A simulação utiliza ratings ilustrativos, definidos para o cenário demonstrativo.

Esses ratings ainda não estão integrados às estimativas históricas produzidas pelo motor Elo.

As frequências de títulos resultantes das simulações não devem ser apresentadas como previsões empiricamente validadas da Copa do Mundo.

A integração entre ratings históricos e simulação está prevista para uma etapa futura.

## 7. Evidências e reprodutibilidade

O projeto utiliza práticas de rastreabilidade e versionamento para permitir a inspeção dos resultados.

Entre os mecanismos adotados estão:

- Histórico de alterações com Git.
- Código-fonte versionado.
- Testes automatizados.
- Snapshot da base histórica.
- Identificação da origem dos dados.
- Verificação de integridade.
- Documentação de decisões metodológicas.
- Separação entre dados observados, resultados calculados e hipóteses experimentais.

Publicações, vídeos e capturas de tela podem servir como evidências complementares, mas não substituem os dados originais, o código reproduzível ou fontes oficiais quando estas forem necessárias.

## 8. Licenças e atribuições

**Dados históricos:** a fonte `martj42/international_results` declara licença CC0 1.0.

**IAPredict:** o projeto é citado como referência do estudo inicial. Este documento não afirma a existência de autorização para reutilização de seu código nem atribui ao Orbia a autoria das implementações originais.

**Orbia Intelligence:** a licença aplicável ao código do próprio repositório deve ser consultada no arquivo de licença correspondente, quando disponível.

As licenças de bibliotecas e dependências permanecem sujeitas às condições de seus respectivos projetos.

## 9. Apresentação profissional

Descrição sugerida para portfólio:

> Desenvolvi o Orbia Intelligence, um laboratório independente de análise de dados de futebol com Python e Streamlit. O projeto inclui processamento auditável de aproximadamente 50 mil registros históricos, estatísticas descritivas, simulação Monte Carlo e um motor experimental de rating Elo com rankings, filtros temporais e evolução histórica. A arquitetura prioriza reprodutibilidade, testes automatizados e transparência metodológica.

A descrição distingue as funcionalidades efetivamente implementadas das etapas futuras de validação preditiva.

## 10. Documentação complementar

- [README principal](../README.md)
- [Roadmap técnico](ROADMAP.md)
- [Documentação dos dados históricos](DADOS_FUTEBOL.md)

---

**Orbia Intelligence — Do histórico à inteligência de jogo.**