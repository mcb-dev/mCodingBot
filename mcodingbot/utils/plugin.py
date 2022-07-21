from __future__ import annotations

import crescent
import typing

if typing.TYPE_CHECKING:
    from mcodingbot.bot import Bot

__all__: typing.Sequence[str] = ("Plugin",)


class Plugin(crescent.Plugin):
    @property
    def app(self) -> Bot:
        # NOTE: Worried that not using `if TYPE_CHECKING` for `Bot` will cause circular
        # imports later down the line.
        return typing.cast("Bot", super().app)
