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

    @staticmethod
    async def add_word(word: str, user_id: int) -> None:
        word_model = await Word.get_or_create(word=word)
        user = await User.get_or_create(user_id=user_id)
        await word_model.users.add(user)

    @staticmethod
    async def delete_word(word: str, user_id: int) -> bool:
        """
        Return `True` if the word was successfully removed from the user.
        Return `False` otherwise.
        """
        user = await User.exists(user_id=user_id)
        if not user:
            return False

        words = await user.words.fetchmany()

        for word_ in words:
            if word_.word == word:
                break
        else:
            return False

        word_model = await Word.exists(word=word)
        if not word_model:
            return False

        await user.words.remove(word_model)
        return True
