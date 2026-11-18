# Orbia Intelligence — V8: Validação Preditiva e Calibração

## 1. Visão geral

A V8 do Orbia Intelligence introduz uma metodologia de avaliação histórica para o motor de previsões baseado em Elo Rating.

O objetivo é verificar se as probabilidades estimadas pelo modelo representam adequadamente os resultados observados em partidas internacionais de futebol.

A implementação contempla geração cronológica de previsões pré-jogo, separação temporal dos dados, comparação com um baseline estatístico, métricas probabilísticas, diagnóstico de calibração e ajuste experimental de parâmetros.

**Os resultados apresentados são históricos e experimentais. Não representam garantia de desempenho em partidas futuras.**

## 2. Base de dados

A avaliação utiliza 49.938 partidas históricas válidas, carregadas a partir do arquivo processado `data/processed/partidas_orbia.csv`.

A origem do histórico é o conjunto público de resultados internacionais mantido pelo projeto `martj42/international_results`, com snapshot versionado no pipeline de dados do Orbia.

### Divisão temporal

| Conjunto | Período | Partidas | Finalidade |
|---|---|---:|---|
| Treinamento | Até 2017 | 41.308 | Estimar parâmetros e baseline |
| Validação | 2018–2021 | 3.562 | Comparar desempenho dos modelos |
| Teste | 2022 em diante | 5.068 | Avaliação final reservada |

A divisão é cronológica, sem embaralhamento aleatório das partidas.

## 3. Previsões sem vazamento temporal

O sistema gera previsões utilizando os ratings Elo disponíveis antes da atualização pelos resultados correspondentes.

Partidas ocorridas na mesma data utilizam ratings congelados no início daquele dia. As atualizações Elo são aplicadas somente após a geração das previsões daquele grupo de partidas.

Essa estratégia impede que o resultado de uma partida do mesmo dia influencie indevidamente outra previsão daquele dia.

O motor Elo utiliza rating inicial de 1.500 pontos e fator K de 20.

## 4. Modelo probabilístico original

A pontuação esperada pelo Elo é calculada por:

\[
E_A = \frac{1}{1 + 10^{(R_B-R_A)/400}}
\]

O modelo original converte essa expectativa em probabilidades de vitória, empate e derrota, utilizando uma taxa de empate equilibrado inicialmente fixada em 25%.

Essa taxa é uma hipótese inicial do modelo, não um parâmetro previamente calibrado.

## 5. Baseline estatístico

Como referência, foi implementado um baseline que utiliza as frequências históricas de vitória, empate e derrota no conjunto de treinamento, com suavização aditiva.

| Resultado | Probabilidade baseline |
|---|---:|
| Vitória | 49,2702% |
| Empate | 22,6671% |
| Derrota | 28,0627% |

O baseline não utiliza ratings Elo nem informações específicas dos confrontos.

## 6. Métricas de avaliação

**Log Loss:** mede a qualidade das probabilidades atribuídas aos resultados efetivamente observados. Penaliza especialmente previsões muito confiantes que estejam erradas.

**Brier Score multiclasse:** calcula a soma dos erros quadráticos das probabilidades das três classes.

**Expected Calibration Error (ECE):** agrupa probabilidades em faixas e compara a confiança média prevista com a frequência observada. É calculado separadamente para vitória, empate e derrota.

Em todas essas métricas, valores menores são preferíveis. O ECE depende da definição das faixas e não substitui Log Loss ou Brier Score.

## 7. Resultado inicial — Elo versus baseline

Avaliação realizada exclusivamente no conjunto de validação de 2018 a 2021.

| Métrica | Elo original | Baseline |
|---|---:|---:|
| Log Loss | 0,899251 | 1,051485 |
| Brier Score | 0,528570 | 0,634166 |

O Elo original apresentou redução relativa aproximada de 14,48% no Log Loss e 16,65% no Brier Score em relação ao baseline.

## 8. Diagnóstico de calibração

A análise identificou um deslocamento sistemático nas probabilidades previstas pelo modelo original.

| Resultado | Previsto | Observado | Diferença |
|---|---:|---:|---:|
| Vitória | 42,15% | 47,73% | −5,58 pp |
| Empate | 20,40% | 23,13% | −2,74 pp |
| Derrota | 37,45% | 29,14% | +8,31 pp |

O modelo subestimava a frequência de vitórias da equipe registrada como mandante e superestimava suas derrotas.

O mesmo padrão geral também foi identificado no período de treinamento, sugerindo um comportamento persistente do modelo.

## 9. Ajuste experimental de probabilidades

Foi implementada uma busca em grade com 42 combinações de parâmetros:

- Ajuste Elo da equipe registrada como mandante: 0, 25, 50, 75, 100, 125 e 150 pontos.
- Taxa de empate equilibrado: 20%, 22,5%, 25%, 27,5%, 30% e 32,5%.

Os parâmetros foram selecionados pela minimização do Log Loss no conjunto de treinamento, sem utilizar validação ou teste para a escolha.

### Parâmetros selecionados

| Parâmetro | Valor |
|---|---:|
| Ajuste Elo da equipe mandante | +75 pontos |
| Taxa de empate equilibrado | 27,5% |
| Log Loss no treinamento ajustado | 0,932394 |

O ajuste é aplicado à geração das probabilidades e não altera os ratings históricos armazenados pelo motor Elo.

## 10. Resultado — Elo original versus ajustado

### Qualidade preditiva

| Métrica | Original | Ajustado | Redução relativa |
|---|---:|---:|---:|
| Log Loss | 0,899251 | 0,880978 | 2,03% |
| Brier Score | 0,528570 | 0,517927 | 2,01% |

### Calibração

| Resultado | ECE original | ECE ajustado |
|---|---:|---:|
| Vitória | 0,061459 | 0,030736 |
| Empate | 0,027360 | 0,016799 |
| Derrota | 0,085859 | 0,027489 |

### Viés global após o ajuste

| Resultado | Previsto | Observado | Diferença |
|---|---:|---:|---:|
| Vitória | 50,27% | 47,73% | +2,55 pp |
| Empate | 21,45% | 23,13% | −1,68 pp |
| Derrota | 28,27% | 29,14% | −0,87 pp |

O modelo ajustado apresentou menores erros probabilísticos e menores ECEs nas três classes durante a validação.

Esses resultados favorecem o ajuste experimental, mas não demonstram superioridade universal nem calibração perfeita.

## 11. Limitações metodológicas

O ajuste de 75 pontos para a equipe registrada como mandante não comprova uma vantagem de jogar em casa. Partidas internacionais podem ocorrer em campo neutro, e a posição da equipe no registro pode refletir características da base histórica.

A busca em grade utiliza um conjunto discreto e limitado de parâmetros. O desempenho no treinamento não constitui uma estimativa independente de generalização.

As métricas apresentadas para validação ainda não incluem intervalos de confiança ou análise de estabilidade por competição e período.

A calibração por ECE é sensível à quantidade de faixas e pode ocultar diferenças dentro de cada agrupamento.

O conjunto de teste de 2022 em diante permanece reservado. Não foi utilizado para selecionar parâmetros, comparar modelos ou tomar decisões de implementação.

## 12. Reprodutibilidade

Executar a suíte de testes:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

Executar a avaliação histórica:

```powershell
.\.venv\Scripts\python.exe -m scripts.avaliar_validacao_futebol
```

Executar o diagnóstico de calibração:

```powershell
.\.venv\Scripts\python.exe -m scripts.avaliar_calibracao_futebol
```

Executar a comparação entre os modelos:

```powershell
.\.venv\Scripts\python.exe -m scripts.comparar_ajuste_futebol
```

**Estado da implementação:** 220 testes automatizados aprovados.

## 13. Próximas etapas

Antes de adotar o modelo ajustado como versão definitiva, o projeto deverá ampliar os diagnósticos de estabilidade, avaliar a influência de partidas em campo neutro e documentar os critérios para a avaliação final no conjunto de teste.

A V8 estabelece a base experimental para evoluções posteriores do Orbia Intelligence, mantendo separadas a construção do modelo, a seleção de parâmetros e a avaliação histórica.