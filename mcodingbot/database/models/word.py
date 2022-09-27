from __future__ import annotations

from apgorm import types, ManyToMany, Unique, Model
from asyncpg.exceptions import UniqueViolationError

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcodingbot.database.models.user import User
    from mcodingbot.database.models.user_word import UserWord


class Word(Model):
    id = types.Serial().field()
    word = types.VarChar(32).field()
    word_unique = Unique(word)

    users = ManyToMany["User", "UserWord"](
        "id", "user_words.word_id", "user_words.user_id", "users.user_id"
    )

    primary_key = (id,)

    @staticmethod
    async def get_or_create(word: str) -> Word:
        try:
            return await Word(word=word).create()
        except UniqueViolationError:
            return await Word.fetch(word=word)
