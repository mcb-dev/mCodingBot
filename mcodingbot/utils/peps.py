from __future__ import annotations

import dataclasses
from logging import getLogger
from typing import TYPE_CHECKING, Sequence

import aiohttp

if TYPE_CHECKING:
    from mcodingbot.bot import Bot

_LOG = getLogger(__name__)

__all__: Sequence[str] = ("PepManager", "Pep")


class PEPManager:
    def __init__(self) -> None:
        self._peps: dict[int, PEPInfo] = {}

    async def fetch_pep_info(self, bot: Bot) -> None:
        async with bot.session.get(
            "https://peps.python.org/api/peps.json"
        ) as resp:
            try:
                resp.raise_for_status()
            except aiohttp.ClientResponseError:
                _LOG.exception("Could not fetch peps.")
            else:
                self._peps = {
                    int(pep_id): PEPInfo(
                        number=int(pep_id),
                        title=pep["title"],
                        authors=pep["authors"],
                        link=pep["url"],
                    )
                    for pep_id, pep in (await resp.json()).items()
                }

    def get(self, pep_number: int) -> PEPInfo | None:
        return self._peps.get(pep_number)


@dataclasses.dataclass
class PEPInfo:
    number: int
    title: str
    authors: str
    link: str

    def __str__(self) -> str:
        return f"PEP {self.number}: {self.title} (<{self.link}>)"
