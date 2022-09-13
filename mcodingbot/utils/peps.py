from __future__ import annotations

import dataclasses
from logging import getLogger
from typing import TYPE_CHECKING, Any, Sequence, final

if TYPE_CHECKING:
    from mcodingbot.bot import Bot

_LOG = getLogger(__name__)

__all__: Sequence[str] = ("PepManager", "Pep")


class PepManager:
    def __init__(self, bot: Bot) -> None:
        self._bot = bot
        self._peps: dict[int, Any] = {}

    async def fetch_pep_info(self) -> None:
        async with self._bot.session.get(
            "https://peps.python.org/api/peps.json"
        ) as resp:
            if resp.status != 200:
                _LOG.warning("Could not fetch peps.")
                return
            self._peps = {
                int(key): value for key, value in (await resp.json()).items()
            }

    def get(self, pep_number: int) -> Pep | None:
        if not (pep := self._peps.get(pep_number)):
            return None
        return Pep(
            number=pep_number,
            title=pep["title"],
            authors=pep["authors"],
            python_version=pep["python_version"],
            link=pep["url"],
        )


@final
@dataclasses.dataclass
class Pep:
    number: int
    title: str
    authors: str
    link: str
    python_version: str | None

    def stringify(self, *, hide_embed: bool) -> str:
        link = f"<{self.link}>" if hide_embed else self.link
        return f"PEP {self.number}: {self.title} ({link})"
