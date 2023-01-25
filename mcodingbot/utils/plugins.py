from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

import crescent
import hikari

if TYPE_CHECKING:
    from mcodingbot.model import Model

__all__: Sequence[str] = ("Context", "Plugin")


class Context(crescent.Context):
    app: hikari.GatewayBot


Plugin = crescent.Plugin[hikari.GatewayBot, "Model"]
