from typing import TYPE_CHECKING
from apgorm import types, ForeignKey, Model
from mcodingbot.database.converters import NumericConverter

from mcodingbot.database.models.word import Word
from mcodingbot.database.models.user import User


class UserWord(Model):
    word_id = types.Serial().field()
    user_id = types.Numeric().field().with_converter(NumericConverter)

    word_id_fk = ForeignKey(word_id, Word.id)
    user_id_fk = ForeignKey(user_id, User.user_id)

    primary_key = (word_id, user_id)
