from __future__ import annotations
from curses.ascii import isdigit

from dataclasses import dataclass
import itertools
from logging import getLogger
from typing import TYPE_CHECKING, Iterable, Iterator, Sequence

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


    def _get_matches_digits(self, query: str, limit: int | None) -> tuple[Iterable[PEPInfo], int | None]:
        """
        Returns a tuple of (Items found, remaining amount of limit).
        """
        items_iter = (value for key, value in self._peps.items() if str(key).startswith(query))
        items = list(itertools.islice(items_iter, limit))
        if limit:
            limit_left = limit - len(items)
        else:
            limit_left = None
        return items, limit_left

    def search(
        self, query: str, *, limit: int | None = None
    ) -> Iterator[PEPInfo]:
        items: Iterable[PEPInfo] = []
        if query.isdigit():
            items, limit = self._get_matches_digits(query, limit)
            yield from items

        res = fuzzy_search(query, self._pep_map, limit=limit)
        for pep in res:
            if pep_info := self.get(pep[2]):
                if pep_info in items:
                    return
                yield pep_info


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
