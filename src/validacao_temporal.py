"""Separação cronológica dos registros pré-jogo da V8."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from src.previsao_pre_jogo import RegistroPreJogo


INICIO_VALIDACAO = date(2018, 1, 1)
INICIO_TESTE = date(2022, 1, 1)


@dataclass(frozen=True)
class DivisaoTemporal:
    """Conjuntos cronológicos para avaliação preditiva."""

    treinamento: tuple[RegistroPreJogo, ...]
    validacao: tuple[RegistroPreJogo, ...]
    teste: tuple[RegistroPreJogo, ...]


def dividir_registros_temporais(
    registros: Iterable[RegistroPreJogo],
    inicio_validacao: date = INICIO_VALIDACAO,
    inicio_teste: date = INICIO_TESTE,
) -> DivisaoTemporal:
    """Divide registros sem sobreposição entre períodos.

    Treinamento: data anterior ao início da validação.
    Validação: início da validação até antes do teste.
    Teste: data igual ou posterior ao início do teste.

    As datas de corte devem ser definidas antes de
    analisar o desempenho no conjunto de teste.
    """

    if (
        type(inicio_validacao) is not date
        or type(inicio_teste) is not date
    ):
        raise ValueError(
            "Os limites temporais devem ser datas válidas."
        )

    if inicio_validacao >= inicio_teste:
        raise ValueError(
            "O início da validação deve anteceder o teste."
        )

    ordenados = sorted(
        registros,
        key=lambda registro: (
            registro.data,
            registro.selecao_casa,
            registro.selecao_fora,
            registro.competicao,
        ),
    )

    treinamento = []
    validacao = []
    teste = []

    for registro in ordenados:
        if registro.data < inicio_validacao:
            treinamento.append(registro)

        elif registro.data < inicio_teste:
            validacao.append(registro)

        else:
            teste.append(registro)

    return DivisaoTemporal(
        treinamento=tuple(treinamento),
        validacao=tuple(validacao),
        teste=tuple(teste),
    )
