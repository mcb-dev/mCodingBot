from __future__ import annotations

import dataclasses
from logging import getLogger
from typing import TYPE_CHECKING, Any, Sequence, final

import aiohttp

if TYPE_CHECKING:
    from mcodingbot.bot import Bot

_LOG = getLogger(__name__)

__all__: Sequence[str] = ("PepManager", "Pep")


class PepManager:
    def __init__(self) -> None:
        self._peps: dict[int, Any] = {}

    async def fetch_pep_info(self, bot: Bot) -> None:
        async with bot.session.get(
            "https://peps.python.org/api/peps.json"
        ) as resp:
            try:
                resp.raise_for_status()
                self._peps = {
                    int(key): value
                    for key, value in (await resp.json()).items()
                }
            except aiohttp.ClientResponseError:
                _LOG.exception("Could not fetch peps.")

    def get(self, pep_number: int) -> Pep | None:
        if not (pep := self._peps.get(pep_number)):
            return None
        return Pep(
            number=pep_number,
            title=pep["title"],
            authors=pep["authors"],
            link=pep["url"],
        )


@final
@dataclasses.dataclass
class Pep:
    number: int
    title: str
    authors: str
    link: str

    def __str__(self) -> str:
        return f"PEP {self.number}: {self.title} (<{self.link}>)"
