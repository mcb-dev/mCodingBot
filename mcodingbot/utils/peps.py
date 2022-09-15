from __future__ import annotations

from dataclasses import dataclass
from logging import getLogger
from typing import TYPE_CHECKING, Generator, Sequence

import aiohttp
import hikari

from mcodingbot.config import CONFIG
from mcodingbot.utils.search import fuzzy_search

if TYPE_CHECKING:
    from mcodingbot.bot import Bot

_LOG = getLogger(__name__)

__all__: Sequence[str] = ("PEPManager", "PEPInfo")


class PEPManager:
    def __init__(self) -> None:
        self._peps: dict[int, PEPInfo] = {}
        self._pep_map: dict[int, str] = {}

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
                self._pep_map = {
                    k: f"{v.title} ({v.number})" for k, v in self._peps.items()
                }

    def get(self, pep_number: int) -> PEPInfo | None:
        return self._peps.get(pep_number)

    def search(
        self, query: str, limit: int = 20
    ) -> Generator[PEPInfo, None, None]:
        res = fuzzy_search(query, self._pep_map, limit=limit)
        return (
            pep_info
            for pep in res
            if (pep_info := self.get(pep[2])) is not None
        )


@dataclass
class PEPInfo:
    number: int
    title: str
    authors: str
    link: str

    def embed(self) -> hikari.Embed:
        return hikari.Embed(
            title=f"PEP {self.number}: {self.title}",
            url=self.link,
            color=CONFIG.theme,
        ).set_author(name=self.authors)

    def __str__(self) -> str:
        return f"PEP {self.number}: [{self.title}]({self.link})"
