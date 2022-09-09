from __future__ import annotations

from apgorm import Model, types
from asyncpg.exceptions import UniqueViolationError

from mcodingbot.database.converters import NumericC


class User(Model):
    user_id = types.Numeric().field().with_converter(NumericC)

    is_donor = types.Boolean().field(default=False)

    primary_key = (user_id,)

    @staticmethod
    async def get_or_create(user_id: int) -> User:
        try:
            return await User(user_id=user_id).create()
        except UniqueViolationError:
            return await User.fetch(user_id=user_id)
