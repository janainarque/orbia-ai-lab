"""Motor experimental de simulação Monte Carlo do Orbia."""

import math
import random
from dataclasses import dataclass
from collections.abc import Sequence


@dataclass(frozen=True)
class Participante:
    nome: str
    rating: float


@dataclass(frozen=True)
class ResultadoSimulacao:
    simulacoes: int
    semente: int
    titulos: dict[str, int]
    probabilidades: dict[str, float]


def validar_rating(rating: float) -> None:
    """Valida um rating fictício no intervalo permitido."""

    if (
        isinstance(rating, bool)
        or not isinstance(rating, (int, float))
        or not math.isfinite(rating)
        or not 0 <= rating <= 3000
    ):
        raise ValueError("Rating inválido.")


def probabilidade_vitoria(
    rating_a: float,
    rating_b: float,
) -> float:
    """Calcula a probabilidade de vitória pelo modelo Elo."""

    validar_rating(rating_a)
    validar_rating(rating_b)

    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def validar_participantes(
    participantes: Sequence[Participante],
) -> None:
    """Valida os quatro participantes do torneio experimental."""

    if len(participantes) != 4:
        raise ValueError(
            "O torneio experimental exige quatro participantes."
        )

    nomes = set()

    for participante in participantes:
        if (
            not isinstance(participante.nome, str)
            or not participante.nome.strip()
        ):
            raise ValueError("Nome de participante inválido.")

        nome_normalizado = participante.nome.strip().casefold()

        if nome_normalizado in nomes:
            raise ValueError("Participantes duplicados.")

        nomes.add(nome_normalizado)
        validar_rating(participante.rating)


def simular_torneios(
    participantes: Sequence[Participante],
    quantidade: int = 10000,
    semente: int = 42,
) -> ResultadoSimulacao:
    """Simula torneios eliminatórios de quatro participantes."""

    validar_participantes(participantes)

    if isinstance(quantidade, bool) or not isinstance(quantidade, int) or quantidade <= 0:
        raise ValueError("Quantidade de simulações inválida.")

    if isinstance(semente, bool) or not isinstance(semente, int):
        raise ValueError("A semente deve ser um número inteiro.")

    gerador = random.Random(semente)

    titulos = {
        participante.nome: 0
        for participante in participantes
    }

    def disputar(
        primeiro: Participante,
        segundo: Participante,
    ) -> Participante:
        chance_primeiro = probabilidade_vitoria(
            primeiro.rating,
            segundo.rating,
        )

        if gerador.random() < chance_primeiro:
            return primeiro

        return segundo

    for _ in range(quantidade):
        semifinal_1 = disputar(
            participantes[0],
            participantes[1],
        )

        semifinal_2 = disputar(
            participantes[2],
            participantes[3],
        )

        campeao = disputar(semifinal_1, semifinal_2)

        titulos[campeao.nome] += 1

    probabilidades = {
        nome: (total / quantidade) * 100
        for nome, total in titulos.items()
    }

    return ResultadoSimulacao(
        simulacoes=quantidade,
        semente=semente,
        titulos=titulos,
        probabilidades=probabilidades,
    )
