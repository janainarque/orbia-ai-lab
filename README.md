# Orbia Intelligence

### Football Data & Analytics Lab

Laboratório independente de análise de futebol que combina dados históricos, estatísticas descritivas, modelagem matemática, visualização interativa e simulações experimentais.

O objetivo é construir, de forma incremental, uma plataforma de inteligência esportiva com foco em qualidade de dados, reprodutibilidade, testes automatizados e transparência metodológica.

**Versão em desenvolvimento: V8 — Predictive Validation & Calibration**

A V7 — Elo Rating Engine está integrada à `main`.

A V8 está em desenvolvimento na branch `feature/predictive-validation`, incorporando validação temporal, métricas probabilísticas, diagnóstico de calibração e ajuste experimental das probabilidades Elo.

O projeto utiliza 49.938 partidas históricas válidas e conta com 220 testes automatizados aprovados.

## Funcionalidades

### 1. Análise histórica de seleções

- Base de partidas internacionais de seleções masculinas.
- Ranking histórico por aproveitamento.
- Filtros por período, competição e mínimo de partidas.
- Indicadores de vitórias, empates, derrotas e gols.
- Comparação visual entre seleções.
- Análise individual de desempenho.

O ranking utiliza três pontos por vitória e um por empate. Ele é descritivo, não representa o ranking oficial da FIFA e não mede diretamente a força relativa das seleções.

### 2. Elo Rating Engine — V7

Motor experimental de avaliação de força relativa de seleções, baseado em resultados históricos de partidas internacionais.

**Metodologia implementada:**

- Rating inicial de 1500 pontos por seleção.
- Fator K fixo de 20 pontos.
- Cálculo do resultado esperado de cada confronto.
- Atualização dos ratings após vitórias, empates e derrotas.
- Processamento cronológico das partidas por data.
- Ordenação determinística para partidas na mesma data.
- Possibilidade de calcular ratings em datas históricas.

**Ranking interativo:**

- Classificação por rating Elo.
- Data de referência configurável.
- Filtro por quantidade mínima de partidas.
- Filtro de atividade recente, com janelas de 365, 730 ou 1095 dias.
- Visualização das 15 primeiras seleções.
- Comparação entre duas seleções, incluindo posições e diferença de rating.

**Evolução histórica:**

- Gráfico interativo da evolução anual dos ratings.
- Comparação de até quatro seleções.
- Seleção do período de análise.
- Preservação do histórico anterior ao período visualizado.
- Consulta aos dados utilizados no gráfico.
- Tratamento de períodos sem partidas e seleções não selecionadas.

Cada ponto da evolução anual representa o último rating registrado em partidas daquele ano. Anos sem partidas não geram novas observações.

O cálculo considera o histórico anterior ao período selecionado, evitando reiniciar artificialmente o rating no primeiro ano exibido.

**Limitações metodológicas:**

O modelo utiliza uma implementação experimental do sistema Elo, sem vantagem de mando, ponderação por competição, ajuste pela diferença de gols ou tratamento específico de disputas por pênaltis.

A ordenação de partidas realizadas na mesma data é determinística, mas não necessariamente corresponde à ordem real dos horários dos confrontos.

Os ratings não representam a classificação oficial da FIFA.

A V8 introduz a avaliação histórica da capacidade preditiva do modelo Elo, incluindo comparação com baseline estatístico, validação temporal e análise de calibração. A avaliação final no conjunto de teste permanece reservada.

### 3. Predictive Validation & Calibration — V8

A V8 introduz uma camada de avaliação preditiva para verificar a qualidade das probabilidades produzidas pelo motor Elo.

**Metodologia implementada:**

- Geração cronológica de previsões pré-jogo.
- Proteção contra vazamento temporal, incluindo partidas realizadas na mesma data.
- Separação temporal entre treinamento, validação e teste.
- Baseline estatístico baseado nas frequências históricas.
- Avaliação por Log Loss e Brier Score multiclasse.
- Diagnóstico de calibração por classe utilizando Expected Calibration Error (ECE).
- Busca em grade para ajuste experimental de probabilidades.
- Testes automatizados e documentação reprodutível.

**Divisão temporal:**

| Conjunto | Período | Partidas |
|---|---|---:|
| Treinamento | Até 2017 | 41.308 |
| Validação | 2018–2021 | 3.562 |
| Teste reservado | 2022 em diante | 5.068 |

**Resultados na validação histórica (2018–2021):**

| Métrica | Elo original | Elo ajustado |
|---|---:|---:|
| Log Loss | 0,899251 | 0,880978 |
| Brier Score | 0,528570 | 0,517927 |
| ECE — Vitória | 0,061459 | 0,030736 |
| ECE — Empate | 0,027360 | 0,016799 |
| ECE — Derrota | 0,085859 | 0,027489 |

Os parâmetros selecionados exclusivamente no treinamento foram:

- Ajuste Elo da equipe registrada como mandante: +75 pontos.
- Taxa de empate equilibrado: 27,5%.

O modelo ajustado apresentou redução relativa aproximada de 2,03% no Log Loss e 2,01% no Brier Score em relação ao Elo original durante a validação.

**Limitações:** o ajuste associado à equipe mandante não comprova vantagem real de jogar em casa, especialmente porque partidas internacionais podem ocorrer em campo neutro. Os resultados são experimentais e não garantem desempenho futuro.

O conjunto de teste permanece reservado e não foi utilizado para seleção dos parâmetros.

**Documentação técnica:** [Validação Preditiva V8](docs/VALIDACAO_PREDITIVA_V8.md).

### 3. Simulador Monte Carlo

Simulador experimental de torneio eliminatório com quatro seleções.

- Execução de múltiplas simulações.
- Frequências estimadas de títulos dentro do cenário simulado.
- Resultados reproduzíveis com semente aleatória.
- Ratings ilustrativos definidos para o experimento.

O simulador ainda não utiliza os ratings históricos calculados pelo Elo Rating Engine.

Seus resultados não constituem previsões empiricamente validadas da Copa do Mundo.

### 4. Análise de probabilidades observadas

Estudo de caso independente baseado em quatro percentuais observados em uma demonstração externa:

- Espanha: 16,9%
- Argentina: 16,4%
- França: 8,0%
- Brasil: 6,4%

Os valores observados somam 47,7%. Os outros 52,3% não estão individualmente disponíveis.

Esses percentuais não foram produzidos pelo motor estatístico do Orbia e não representam uma distribuição completa.

## Engenharia de dados

A infraestrutura histórica foi desenvolvida com foco em rastreabilidade, auditoria e reprodução dos resultados.

| Indicador | Resultado |
|---|---:|
| Registros originais | 49.940 |
| Registros aprovados | 49.938 |
| Registros em quarentena | 2 |
| Testes automatizados aprovados durante o desenvolvimento da V7 | 127 |

Os dois registros conflitantes foram isolados, sem escolher arbitrariamente um dos placares.

A base processada pode ser reconstruída a partir de um snapshot versionado, inclusive sem acesso à fonte externa.

O conjunto histórico utilizado nesta versão contém partidas registradas até 06/10/2026.

Consulte [DADOS_FUTEBOL.md](docs/DADOS_FUTEBOL.md) para detalhes de origem, integridade, auditoria e limitações.

## Tecnologias

- Python 3.12
- Streamlit
- Pandas
- Altair
- unittest
- Git e GitHub Actions
- Docker (opcional)

## Executar localmente

### 1. Clonar o repositório

```powershell
git clone https://github.com/janainarque/orbia-ai-lab.git
cd orbia-ai-lab
```

### 2. Criar o ambiente virtual

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar as dependências

```powershell
python -m pip install -r requirements.txt
```

### 4. Reconstruir a base histórica

```powershell
python -m scripts.reconstruir_base_futebol
```

### 5. Executar o dashboard

```powershell
python -m streamlit run app.py
```

Acesse http://localhost:8501.

### Docker (opcional)

```powershell
docker compose up --build
```

A reconstrução da base histórica também deve ser realizada no ambiente em que a aplicação será executada, quando os arquivos processados ainda não existirem.

## Testes automatizados

Execute a suíte completa:

```powershell
python -m unittest discover -s tests -v
```

Durante o desenvolvimento da V7, a suíte alcançou 127 testes aprovados, abrangendo:

- Validação e transformação de dados.
- Importação e auditoria da base histórica.
- Recuperação do snapshot.
- Estatísticas descritivas e ranking histórico.
- Simulação Monte Carlo.
- Cálculo e atualização de ratings Elo.
- Geração de rankings Elo.
- Filtros históricos e de atividade.
- Evolução anual dos ratings.

A execução final da suíte será realizada antes da publicação da V7.

## Limitações atuais

- A base histórica é uma compilação comunitária, não um registro oficial certificado.
- A cobertura varia entre seleções e períodos.
- A base inclui equipes históricas, territoriais e regionais.
- O ranking por aproveitamento não ajusta a dificuldade dos adversários.
- O ranking Elo utiliza parâmetros fixos e ainda não passou por validação preditiva.
- O simulador Monte Carlo utiliza ratings ilustrativos, independentes do motor Elo.
- Ainda não existe avaliação retrospectiva formal das probabilidades produzidas pelo modelo Elo.
- As probabilidades observadas no estudo de caso externo são parciais.

## Próximas evoluções

### V8 — Validação preditiva

- Avaliação temporal do modelo Elo.
- Prevenção de vazamento de informações futuras.
- Estimativa de probabilidades de confrontos.
- Comparação com modelos de referência.
- Avaliação de calibração e Brier Score.
- Investigação da sensibilidade dos parâmetros.

### V9 — Simulação orientada por dados

- Integração dos ratings históricos ao simulador.
- Substituição dos ratings ilustrativos por estimativas.
- Avaliação de diferentes modelos de resultados.
- Simulação de cenários de torneios.
- Apresentação de incertezas e limitações.

Consulte o [Roadmap técnico](docs/ROADMAP.md) para acompanhar o planejamento completo.

## Fontes e créditos

### Dados históricos

[International Football Results — martj42](https://github.com/martj42/international_results)

Licença declarada pela fonte: CC0 1.0.

O Orbia utiliza um snapshot identificado por commit e SHA-256, conforme documentado em `docs/DADOS_FUTEBOL.md`.

### Estudo de caso original

A análise inicial de probabilidades foi motivada por uma demonstração do projeto [IAPredict — Copa 2026](https://github.com/marcovsilva/iapredict-copa2026), desenvolvido por Marcos Vinicius da Silva.

O Orbia é uma implementação independente. Nenhum código do pipeline original foi incorporado ao projeto.

Consulte também:

- [Origem e créditos](docs/ORIGEM_E_CREDITOS.md)
- [Roadmap técnico](docs/ROADMAP.md)

---

**Orbia Intelligence — Do histórico à inteligência de jogo.**