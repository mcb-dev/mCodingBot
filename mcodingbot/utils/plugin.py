from __future__ import annotations

import typing

import crescent

if typing.TYPE_CHECKING:
    from mcodingbot.bot import Bot

__all__: typing.Sequence[str] = ("Plugin",)


class Plugin(crescent.Plugin):
    @property
    def app(self) -> Bot:
        return typing.cast("Bot", super().app)
