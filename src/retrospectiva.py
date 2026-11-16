"""Análise de um ranking PARCIAL de probabilidades observado em vídeo.

Não é um simulador de Copa, não treina modelos e não reutiliza código do bootcamp.
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Previsao:
    selecao: str
    percentual: float


def carregar_ranking(caminho: Path) -> list[Previsao]:
    """Lê ranking parcial em percentuais, sem exigir soma de 100%."""
    linhas: list[Previsao] = []
    nomes: set[str] = set()
    with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if not leitor.fieldnames or not {"selecao", "probabilidade_percentual"}.issubset(leitor.fieldnames):
            raise ValueError("CSV requer colunas selecao e probabilidade_percentual")
        for numero, linha in enumerate(leitor, start=2):
            nome = (linha.get("selecao") or "").strip()
            if not nome or nome.casefold() in nomes:
                raise ValueError(f"Seleção vazia ou duplicada na linha {numero}")
            try:
                valor = float((linha.get("probabilidade_percentual") or "").replace(",", "."))
            except ValueError as exc:
                raise ValueError(f"Percentual inválido na linha {numero}") from exc
            if not math.isfinite(valor) or not 0 <= valor <= 100:
                raise ValueError(f"Percentual fora de 0 a 100 na linha {numero}")
            nomes.add(nome.casefold())
            linhas.append(Previsao(nome, valor))
    if not linhas:
        raise ValueError("Ranking vazio")
    if sum(item.percentual for item in linhas) > 100.01:
        raise ValueError("Percentuais parciais não podem exceder 100%")
    return sorted(linhas, key=lambda item: (-item.percentual, item.selecao))


def resumo(ranking: list[Previsao], campeao_informado: str) -> dict[str, object]:
    """Resume o recorte observado; não calcula métricas que exigem todas as seleções."""
    if not ranking:
        raise ValueError("Ranking vazio")
    if not campeao_informado.strip():
        raise ValueError("Campeão informado não pode estar vazio")
    lider = ranking[0]
    campeao = next((p for p in ranking if p.selecao.casefold() == campeao_informado.casefold()), None)
    return {
        "favorito": lider.selecao,
        "probabilidade_favorito": lider.percentual,
        "campeao_informado": campeao_informado,
        "campeao_esta_no_recorte": campeao is not None,
        "favorito_corresponde_ao_campeao": lider.selecao.casefold() == campeao_informado.casefold(),
        "margem_primeiro_segundo_pp": round(lider.percentual - ranking[1].percentual, 3) if len(ranking) > 1 else None,
        "probabilidade_restante_nao_exibida": round(100 - sum(p.percentual for p in ranking), 3),
        "limitacao": "Recorte parcial do ranking observado em vídeo; não permite Brier multiclasse nem avaliação de calibração.",
    }
