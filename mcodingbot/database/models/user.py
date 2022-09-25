from __future__ import annotations

from apgorm import ForeignKey, ManyToMany, Model, Unique, types
from asyncpg.exceptions import UniqueViolationError

from mcodingbot.database.converters import NumericConverter


class User(Model):
    user_id = types.Numeric().field().with_converter(NumericConverter)
    is_donor = types.Boolean().field(default=False)
    words = ManyToMany["UserWord", "Word"](
        "user_id", "user_words.user_id", "user_words.word_id", "words.id"
    )

    primary_key = (user_id,)

    @staticmethod
    async def get_or_create(user_id: int) -> User:
        try:
            return await User(user_id=user_id).create()
        except UniqueViolationError:
            return await User.fetch(user_id=user_id)


class Word(Model):
    id = types.Serial().field()
    word = types.VarChar().field()
    word_unique = Unique(word)

    users = ManyToMany["UserWord", "User"](
        "id", "user_words.word_id", "user_words.user_id", "users.user_id"
    )

    primary_key = (id,)

    @staticmethod
    async def create_or_add_user(word: str, user_id: int) -> Word:
        if await Word.exists(word=word):
            return await Word(word=word).create()
        word_model = await Word.fetch(word=word)
        await word_model.users.add(await User.get_or_create(user_id))
        return word_model

    @staticmethod
    async def delete_or_remove_user(word: str, user_id: int) -> bool:
        """Return `True` if the word was successfully removed from the user."""
        user = await User.fetch(user_id=user_id)
        if not user.words:
            return False

        word_model = await Word.fetch(word=word)
        await word_model.users.add(await User.get_or_create(user_id))
        return word_model



class UserWord(Model):
    word_id = types.Serial().field()
    user_id = types.Serial().field()

    word_id_fk = ForeignKey(word_id, Word.id)
    user_id_fk = ForeignKey(user_id, User.user_id)

    primary_key = (word_id, user_id)
