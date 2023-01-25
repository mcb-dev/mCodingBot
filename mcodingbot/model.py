from __future__ import annotations

import logging

import aiohttp
import hikari

from mcodingbot.config import CONFIG
from mcodingbot.database.database import Database

_LOG = logging.getLogger(__name__)


def _warn_missing_config(variable: str, feature: str) -> None:
    _LOG.warning(f"`{variable}` is required to {feature}.")


class Model:
    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None
        self._db: Database | None = None

        if not CONFIG.mcoding_server:
            _LOG.warning(
                "Server stats and donor roles will not be updated because"
                " `mcoding_server` is not provided. Is this intended?"
            )
        else:
            if not CONFIG.sub_count_channel:
                _warn_missing_config("sub_count_channel", "post sub count stats")
            if not CONFIG.view_count_channel:
                _warn_missing_config("view_count_channel", "post view count stats")
            if not CONFIG.member_count_channel:
                _warn_missing_config("member_count_channel", "post member count stats")
            if not CONFIG.donor_role:
                _warn_missing_config("donor_role", "update donor roles")

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

    async def on_start(self, _: hikari.StartedEvent) -> None:
        self._session = aiohttp.ClientSession()
        if not CONFIG.no_db_mode:
            self._db = await Database.create()
        else:
            _LOG.warning("Running bot without database.")

    async def on_stop(self, _: hikari.StoppedEvent) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
