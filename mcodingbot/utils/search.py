from __future__ import annotations

from typing import Mapping, TypeVar

from rapidfuzz import fuzz, process

K = TypeVar("K")
V = TypeVar("V")


def fuzzy_search(
    query: str,
    choices: Mapping[K, V],
    *,
    score_cutoff: int | float | None = None,
    limit: int | None = None,
) -> list[tuple[V, float, K]]:
    return process.extract(
        query,
        choices=choices,
        scorer=fuzz.WRatio,
        score_cutoff=score_cutoff,
        limit=limit,
    )
