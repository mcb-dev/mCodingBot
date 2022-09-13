from __future__ import annotations

from typing import Any

import aiohttp
import crescent
import hikari

from mcodingbot.config import CONFIG
from mcodingbot.database.database import Database


class Bot(crescent.Bot):
    def __init__(self) -> None:
        super().__init__(
            token=CONFIG.discord_token,
            intents=(
                hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.GUILD_MEMBERS
            ),
        )

        self.plugins.load_folder("mcodingbot.plugins")

        self._session: aiohttp.ClientSession | None = None
        self._db: Database | None = None

    @property
    def session(self) -> aiohttp.ClientSession:
        if not self._session:
            raise AttributeError("Session has not been set yet.")
        return self._session

    @property
    def db(self) -> Database:
        if not self._db:
            raise AttributeError("Database has not been set yet.")
        return self._db

    async def start(self, *args: Any, **kwargs: Any) -> None:
        self._session = aiohttp.ClientSession()
        self._db = await Database.create()

        await super().start(*args, **kwargs)

    async def join(self, *args: Any, **kwargs: Any) -> None:
        await super().join(*args, **kwargs)
        if self._session and not self._session.closed:
            await self._session.close()
