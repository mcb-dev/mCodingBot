from __future__ import annotations

import logging
from typing import TypeVar

import apgorm

from mcodingbot.config import CONFIG
from mcodingbot.database.models import Highlight, User, UserHighlight

_LOGGER = logging.getLogger(__name__)
_SELF = TypeVar("_SELF", bound="Database")


class Database(apgorm.Database):
    users = User
    user_highlights = UserHighlight
    highlights = Highlight

    def __init__(self) -> None:
        super().__init__("mcodingbot/database/migrations")

    async def open(self) -> None:
        await self.connect(
            host="localhost",
            database="mcodingbot",
            user="mcodingbot",
            password=CONFIG.db_password,
        )
        if self.must_create_migrations():
            _LOGGER.info("Creating migrations...")
            self.create_migrations()
        if await self.must_apply_migrations():
            _LOGGER.info("Applying migrations...")
            await self.apply_migrations()
