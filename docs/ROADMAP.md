# Orbia Intelligence — Roadmap técnico

Este documento acompanha a evolução do Orbia Intelligence,
um laboratório independente de análise de dados e
simulação estatística aplicada ao futebol.

## V1–V4 — Fundação e análise descritiva

**Status: concluído**

- [x] Estrutura inicial do projeto Python
- [x] Dashboard interativo com Streamlit
- [x] Estudo de caso independente de probabilidades observadas
- [x] Validação de dados e regras de negócio
- [x] Indicadores estatísticos descritivos
- [x] Testes automatizados
- [x] Documentação de origem e créditos

## V5 — Simulação Monte Carlo

**Status: concluído**

- [x] Motor experimental de simulação
- [x] Torneio eliminatório com quatro seleções
- [x] Ratings ilustrativos
- [x] Simulações reproduzíveis por semente
- [x] Cálculo de frequências de títulos simulados
- [x] Integração ao dashboard
- [x] Testes automatizados

**Limitação:** os ratings são ilustrativos e não foram
estimados a partir dos resultados históricos.

## V6.1 — Infraestrutura histórica

**Status: concluído**

- [x] Identificação de fonte histórica de partidas
- [x] Snapshot versionado da base original
- [x] Verificação de integridade por SHA-256
- [x] Validação e transformação dos registros
- [x] Auditoria de duplicidades e conflitos
- [x] Quarentena de registros inconsistentes
- [x] Reconstrução reproduzível da base
- [x] Recuperação offline
- [x] Documentação de proveniência

Resultado: 49.938 partidas aprovadas e dois registros
conflitantes preservados em quarentena.

## V6.2 — Historical Football Analytics

**Status: concluído e integrado à main**

- [x] Estatísticas individuais por seleção
- [x] Vitórias, empates e derrotas
- [x] Gols marcados, sofridos e saldo
- [x] Pontuação e aproveitamento
- [x] Ranking histórico por aproveitamento
- [x] Critérios determinísticos de desempate
- [x] Filtros por período e competição
- [x] Quantidade mínima de partidas
- [x] Dashboard histórico interativo
- [x] Gráfico comparativo de seleções
- [x] Análise individual de desempenho
- [x] Atualização da identidade visual
- [x] Testes automatizados: 79 aprovados
- [x] Revisão final e merge na main

**Limitação:** o ranking é descritivo e não ajusta
a força dos adversários.


## V7 — Elo Rating Engine

**Status: implementado — publicação pendente**

### Motor Elo
- [x] Definir metodologia de rating Elo experimental
- [x] Implementar rating inicial de 1500 pontos
- [x] Implementar fator K de 20 pontos
- [x] Processar partidas em ordem cronológica
- [x] Calcular resultados esperados de cada confronto
- [x] Atualizar ratings após vitórias, empates e derrotas
- [x] Garantir resultados determinísticos

### Ranking e filtros
- [x] Criar ranking de força separado do aproveitamento
- [x] Permitir seleção de data de referência
- [x] Filtrar por quantidade mínima de partidas
- [x] Filtrar seleções por atividade recente
- [x] Implementar comparação entre duas seleções

### Dashboard e evolução histórica
- [x] Criar aba Ranking Elo no Streamlit
- [x] Exibir classificação e gráfico Top 15
- [x] Implementar evolução histórica anual dos ratings
- [x] Permitir comparação de até quatro seleções
- [x] Implementar filtro de período histórico
- [x] Preservar o histórico anterior ao período visualizado
- [x] Tratar seleções vazias e períodos sem partidas
- [x] Validar o funcionamento com datas anteriores a 2000

### Qualidade e publicação
- [x] Implementar testes automatizados
- [x] Executar 127 testes com sucesso durante o desenvolvimento
- [x] Validar o funcionamento da interface
- [ ] Atualizar documentação da V7
- [ ] Executar testes finais
- [ ] Criar commit e Pull Request
- [ ] Integrar à main

### Limitações e pesquisas futuras
- [ ] Investigar efeitos do mando de campo
- [ ] Avaliar sensibilidade dos parâmetros Elo
- [ ] Avaliar ponderação por competição
- [ ] Validar capacidade preditiva do modelo

**Nota:** o ranking Elo é experimental e não corresponde
ao ranking oficial da FIFA. Ainda não foram aplicados
ajustes por mando de campo, competição ou diferença de gols.
A capacidade preditiva será avaliada na V8.

## V8 — Validação preditiva

**Status: planejado**

- [ ] Definir protocolo de avaliação temporal
- [ ] Evitar vazamento de informações futuras
- [ ] Estimar probabilidades de confrontos
- [ ] Comparar resultados com modelos de referência
- [ ] Avaliar calibração das probabilidades
- [ ] Calcular métricas apropriadas, como Brier Score
- [ ] Documentar limitações e incertezas

## V9 — Simulação orientada por dados

**Status: planejado**

- [ ] Integrar ratings históricos ao simulador
- [ ] Substituir ratings ilustrativos por estimativas
- [ ] Avaliar modelos de resultados de partidas
- [ ] Simular diferentes cenários de torneios
- [ ] Apresentar probabilidades e incertezas
- [ ] Testar reprodutibilidade e consistência

## Evoluções complementares

- [ ] Melhorar acessibilidade e responsividade
- [ ] Consolidar e organizar o CSS
- [ ] Aprimorar documentação técnica
- [ ] Implementar observabilidade
- [ ] Avaliar recursos explicativos com IA
- [ ] Revisar segurança e dependências
- [ ] Preparar demonstração pública do projeto

## Princípios do projeto

1. Dados rastreáveis e auditáveis.
2. Separação entre estatísticas e previsões.
3. Modelos reproduzíveis e testáveis.
4. Transparência sobre limitações.
5. Evolução incremental e documentação contínua.

---

Orbia Intelligence — Do histórico à inteligência de jogo.
