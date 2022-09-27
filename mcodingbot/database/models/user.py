from __future__ import annotations
from typing import TYPE_CHECKING

from apgorm import ManyToMany, Model, types
from asyncpg.exceptions import UniqueViolationError

from mcodingbot.database.converters import NumericConverter

from mcodingbot.database.models.word import Word

if TYPE_CHECKING:
    from mcodingbot.database.models.user_word import UserWord


class User(Model):
    user_id = types.Numeric().field().with_converter(NumericConverter)
    is_donor = types.Boolean().field(default=False)
    words = ManyToMany["Word", "UserWord"](
        "user_id", "user_words.user_id", "user_words.word_id", "words.id"
    )

    primary_key = (user_id,)

    @staticmethod
    async def get_or_create(user_id: int) -> User:
        try:
            return await User(user_id=user_id).create()
        except UniqueViolationError:
            return await User.fetch(user_id=user_id)
