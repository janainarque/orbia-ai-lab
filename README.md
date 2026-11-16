# Orbia AI Lab · Copa 2026

**Status:** MVP independente / protótipo de retrospectiva. **Nome provisório.**

> Previsão vs. realidade: o que um ranking probabilístico dizia antes do resultado e como interpretar o acerto da seleção favorita.

## O que funciona nesta versão

- Dashboard Streamlit com as quatro probabilidades observadas na gravação enviada pela participante.
- Comparação entre a seleção favorita do recorte (Espanha, 16,9%) e o campeão informado no carrossel.
- Validação de CSV, margem entre primeiro e segundo lugar e explicitação dos 52,3% não exibidos.
- Testes automatizados e workflow CI.
- Sem banco, chave de API ou execução de modelos serializados.

**Não é um modelo preditivo novo.** Esta versão não executa ELO, Poisson, Monte Carlo ou agentes; esses elementos aparecem no IAPredict de origem e poderão orientar uma implementação futura independente, mediante definição de escopo e permissões.

## Executar localmente

```powershell
cd Orbia_AI_Lab_MVP
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Acesse `http://localhost:8501`.

**Com Docker Desktop:**

```powershell
docker compose up --build
```

**Testes (sem instalar dependências):**

```powershell
python -m unittest discover -s tests -v
```

## Dados e limites

O arquivo `data/ranking_observado_video.csv` é uma **transcrição de quatro valores mostrados no vídeo**, não um snapshot completo exportado do modelo. A gravação exibe Espanha 16,9%, Argentina 16,4%, França 8,0% e Brasil 6,4%. A soma é 47,7%, portanto não é apropriado calcular Brier multiclasse com esse recorte.

A gravação mostra uma data no computador, mas isso **não comprova por si só** a data de geração do ranking. A confirmação de publicação anterior ao resultado depende dos registros originais e suas datas.

## Origem e créditos

Este protótipo foi criado para desenvolver um estudo de caso independente a partir da experiência de bootcamp com **IAPredict — Copa 2026**, originalmente desenvolvido por **Marcos Vinicius da Silva**: [repositório de referência](https://github.com/marcovsilva/iapredict-copa2026).

Nenhum arquivo de código do IAPredict original está incluído aqui. **Não apresentar este MVP como autoria do pipeline original.** Antes de distribuir código derivado do bootcamp, verificar as permissões e preservar toda a cadeia de créditos.

Leia `docs/ORIGEM_E_CREDITOS.md` e `docs/ROADMAP.md`.
