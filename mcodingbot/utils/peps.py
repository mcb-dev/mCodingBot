from __future__ import annotations

import itertools
from dataclasses import dataclass
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

    def _get_matches_digits(
        self, query: str, limit: int | None
    ) -> tuple[list[PEPInfo], int]:
        """
        Returns a tuple of (Items found, Amount of items found).
        """
        items_iter = (
            value
            for key, value in self._peps.items()
            if str(key).startswith(query)
        )
        items = list(itertools.islice(items_iter, limit))
        return items, len(items)

    def search(
        self, query: str, *, limit: int | None = None
    ) -> Iterator[PEPInfo]:
        yielded = 0

        items: Iterable[PEPInfo] = ()
        if query.isdigit():
            items, yielded = self._get_matches_digits(query, limit)
            yield from items

        if limit and yielded >= limit:
            return

        res = fuzzy_search(query, self._pep_map, limit=limit)

        for pep in res:
            pep_info = self.get(pep[2])
            if not pep_info or pep_info in items:
                continue

            yield pep_info
            yielded += 1

            if limit and yielded >= limit:
                return


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

    @property
    def truncated_title(self) -> str:
        pep_digits = len(str(self.number))

        # 3 is the length two parenthesis and the space used to seperate the
        # pep number from the pep title.
        max_name_length = 100 - pep_digits - 3

        name = self.title
        if len(name) > max_name_length:
            # An extra 3 chars need to be removed to make space for the
            # ellipsis.
            name = f"{self.title[:max_name_length - 3]}..."

        return f"{name} ({self.number})"

    def __str__(self) -> str:
        return f"PEP {self.number}: [{self.title}]({self.link})"
