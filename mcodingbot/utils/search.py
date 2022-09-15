from __future__ import annotations

from collections.abc import Mapping
from typing import TypeVar

from rapidfuzz import fuzz, process


K = TypeVar("K")
V = TypeVar("V")


def find(
    query: str,
    choices: Mapping[K, V],
    score_cutoff: int | float | None = None,
    limit: int = 10,
) -> list[tuple[V, float, K]]:
    return process.extract(
        query,
        choices=choices,
        scorer=fuzz.WRatio,
        score_cutoff=score_cutoff,
        limit=limit,
    )
