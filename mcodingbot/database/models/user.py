from __future__ import annotations

from typing import TYPE_CHECKING

from apgorm import ManyToMany, Model, types
from asyncpg.exceptions import UniqueViolationError

from mcodingbot.database.converters import NumericConverter
from mcodingbot.database.models.highlight import Highlight

if TYPE_CHECKING:
    from mcodingbot.database.models.user_highlight import UserHighlight


class User(Model):
    user_id = types.Numeric().field().with_converter(NumericConverter)
    is_donor = types.Boolean().field(default=False)
    highlights: ManyToMany[Highlight, UserHighlight] = ManyToMany(
        "user_id",
        "user_highlights.user_id",
        "user_highlights.highlight_id",
        "highlights.id",
    )

    primary_key = (user_id,)

    @staticmethod
    async def get_or_create(user_id: int) -> User:
        try:
            return await User(user_id=user_id).create()
        except UniqueViolationError:
            return await User.fetch(user_id=user_id)
