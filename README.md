# Orbia Intelligence

### Football Data & Analytics Lab

Laboratório independente de análise de futebol que combina dados históricos, estatísticas descritivas, visualização interativa e simulações experimentais.

O objetivo é construir, de forma incremental, uma plataforma de inteligência esportiva com foco em qualidade de dados, reprodutibilidade, testes automatizados e transparência metodológica.

**Versão atual: V6.2 — Historical Football Analytics**

## Funcionalidades

### 1. Análise histórica de seleções

- Base de partidas internacionais de seleções masculinas.
- Ranking histórico por aproveitamento.
- Filtros por período, competição e mínimo de partidas.
- Indicadores de vitórias, empates, derrotas e gols.
- Comparação visual entre seleções.
- Análise individual de desempenho.

O ranking utiliza três pontos por vitória e um por empate. Ele não representa o ranking oficial da FIFA nem mede diretamente a força relativa das seleções.

### 2. Simulador Monte Carlo

Simulador experimental de torneio eliminatório com quatro seleções.

- Execução de múltiplas simulações.
- Probabilidades estimadas de título dentro do cenário.
- Resultados reproduzíveis com semente aleatória.
- Ratings ilustrativos definidos para o experimento.

Os ratings ainda não são calculados a partir da base histórica. Os resultados não constituem previsões empiricamente validadas da Copa do Mundo.

### 3. Análise de probabilidades observadas

Estudo de caso independente baseado em quatro percentuais observados em uma demonstração externa:

- Espanha: 16,9%
- Argentina: 16,4%
- França: 8,0%
- Brasil: 6,4%

Os valores observados somam 47,7%. Os outros 52,3% não estão individualmente disponíveis.

Esses percentuais não foram produzidos pelo motor estatístico do Orbia e não representam uma distribuição completa.

## Engenharia de dados

A infraestrutura histórica foi desenvolvida com foco em rastreabilidade.

| Indicador | Resultado |
|---|---:|
| Registros originais | 49.940 |
| Registros aprovados | 49.938 |
| Registros em quarentena | 2 |
| Testes automatizados | 79 |

Os dois registros conflitantes foram isolados, sem escolher arbitrariamente um dos placares.

A base processada pode ser reconstruída a partir de um snapshot versionado, inclusive sem acesso à fonte externa.

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

```powershell
python -m unittest discover -s tests -v
```

A suíte da V6.2 possui 79 testes, incluindo validação de dados, importação, auditoria, estatísticas, ranking, simulação e recuperação do snapshot.

## Limitações atuais

- A base histórica é uma compilação comunitária, não um registro oficial certificado.
- A cobertura varia entre seleções e períodos.
- O ranking por aproveitamento não ajusta a dificuldade dos adversários.
- O simulador utiliza ratings ilustrativos.
- Ainda não existe um modelo preditivo treinado e validado retrospectivamente a partir da base histórica.
- As probabilidades observadas no estudo de caso externo são parciais.

## Próximas evoluções

- Modelo de rating Elo baseado em partidas históricas.
- Validação temporal dos ratings.
- Avaliação de previsões com métricas apropriadas.
- Simulação de confrontos utilizando parâmetros estimados.
- Evolução da experiência visual e da documentação.

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
