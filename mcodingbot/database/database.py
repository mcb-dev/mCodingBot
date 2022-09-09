from __future__ import annotations

import logging

import apgorm

from mcodingbot.config import CONFIG
from mcodingbot.database.models.user import User

LOGGER = logging.getLogger(__name__)


class Database(apgorm.Database):
    users = User

    @staticmethod
    async def create() -> Database:
        db = Database("mcodingbot/database/migrations")
        await db.connect(
            host="localhost",
            database="mcodingbot",
            user="mcodingbot",
            password=CONFIG.db_password,
        )
        if db.must_create_migrations():
            LOGGER.info("Creating migrations...")
            db.create_migrations()
        if await db.must_apply_migrations():
            LOGGER.info("Applying migrations...")
            await db.apply_migrations()

        return db
