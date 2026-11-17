
# Base histórica de futebol — Orbia Intelligence

## 1. Objetivo

A V6.1 estabelece a infraestrutura de dados históricos
para futuras análises estatísticas de seleções nacionais.

Esta etapa não implementa um modelo preditivo empírico.

## 2. Origem dos dados

Projeto: International Football Results

Autor/repositório: martj42/international_results

Fonte:
https://github.com/martj42/international_results

Licença declarada pelo projeto: CC0 1.0

Arquivo original: results.csv

Commit utilizado:
b0948cb558c927c357db4067eac5b37b96d0e4bb

SHA-256 do CSV original:
09AAC809E317F3004C69720A38ADDB656C49EBB19F1937DEAB96F96E3362257A

Os dados representam resultados históricos compilados
de partidas internacionais de seleções masculinas.

A base é uma compilação comunitária, não um registro
oficial certificado pelas federações.

## 3. Auditoria de qualidade

Registros originais: 49.940

Registros aprovados: 49.938

Registros em quarentena: 2

Grupos de duplicidade identificados: 1

Foi encontrada uma ocorrência conflitante:

Data: 1974-02-17
Seleções: Tahiti x New Caledonia
Competição: Friendly

Placares registrados:
- 2 x 1
- 1 x 2

Os dois registros foram preservados em quarentena.

Não foi possível determinar, apenas com os dados
disponíveis, qual placar seria correto ou se houve
duas partidas distintas.

Nenhum placar foi escolhido arbitrariamente.

## 4. Organização dos arquivos

data/raw/
- CSV original obtido da fonte.

data/processed/
- CSV auditado sem os registros conflitantes.
- CSV transformado para o formato interno do Orbia.

data/quarantine/
- Registros separados para investigação.

data/snapshots/
- Cópia compactada do CSV original, preservada
  para permitir a recuperação independente da fonte.

Os diretórios raw, processed e quarantine não são
versionados no Git.

## 5. Reconstrução da base

Executar na raiz do projeto:

    python -m scripts.reconstruir_base_futebol

O processo:

1. Verifica a existência do CSV local.
2. Caso necessário, recupera o snapshot próprio.
3. Na ausência de ambos, tenta a fonte original.
4. Confere o SHA-256 do arquivo.
5. Executa a auditoria de duplicidades.
6. Separa os registros conflitantes.
7. Importa e valida os registros aprovados.

A reconstrução exige os totais de referência da V6.1.

## 6. Testes

Executar:

    python -m unittest discover -s tests -v

A suíte inclui testes de importação, validação,
auditoria e recuperação offline.

## 7. Limitações

- A base pode conter erros não identificados.
- A ausência de duplicidades não comprova a
  exatidão histórica de todos os resultados.
- Os placares da fonte incluem prorrogação quando
  aplicável, mas não disputas de pênaltis.
- A cobertura histórica varia entre seleções e épocas.
- Os resultados não devem ser interpretados como
  probabilidades de vitória ou de título.
- O simulador anterior do Orbia utiliza ratings
  ilustrativos, ainda não estimados desta base.

## 8. Próximas etapas

- Exploração estatística dos resultados históricos.
- Definição de recortes temporais e critérios
  de seleção de partidas.
- Construção de ratings baseados em dados.
- Validação temporal e avaliação do modelo.
- Integração dos resultados ao dashboard.
