from __future__ import annotations

from apgorm import types, ManyToMany, Unique, Model
from asyncpg.exceptions import UniqueViolationError

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcodingbot.database.models.user import User
    from mcodingbot.database.models.user_highlight import UserHighlight


class Highlight(Model):
    id = types.Serial().field()
    highlight = types.VarChar(32).field()
    highlight_unique = Unique(highlight)

    users = ManyToMany["User", "UserHighlight"](
        "id", "user_highlights.highlight_id", "user_highlights.user_id", "users.user_id"
    )

    primary_key = (id,)

    @staticmethod
    async def get_or_create(highlight: str) -> Highlight:
        try:
            return await Highlight(highlight=highlight).create()
        except UniqueViolationError:
            return await Highlight.fetch(highlight=highlight)
