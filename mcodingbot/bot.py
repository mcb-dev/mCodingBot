from __future__ import annotations

import asyncio
from typing import Any

import aiohttp
import crescent

from mcodingbot.config import CONFIG
from mcodingbot.tasks.stats import loop_update_channels


class Bot(crescent.Bot):
    def __init__(self) -> None:
        super().__init__(token=CONFIG.discord_token)

        self.plugins.load("mcodingbot.plugins.info")
        self.plugins.load("mcodingbot.plugins.reactions")

        self._session: aiohttp.ClientSession | None = None

    @property
    def session(self) -> aiohttp.ClientSession:
        if not self._session:
            raise AttributeError("Session has not been set yet.")
        return self._session

    async def start(self, *args: Any, **kwargs: Any) -> None:
        self._session = aiohttp.ClientSession()
        await super().start(*args, **kwargs)

        asyncio.create_task(loop_update_channels(self))

    async def join(self, *args: Any, **kwargs: Any) -> None:
        await super().join(*args, **kwargs)
        if self._session and not self._session.closed:
            await self._session.close()
