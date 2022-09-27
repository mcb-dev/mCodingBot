from typing import TYPE_CHECKING
from apgorm import types, ForeignKey, Model
from mcodingbot.database.converters import NumericConverter

from mcodingbot.database.models.highlight import Highlight
from mcodingbot.database.models.user import User


class UserHighlight(Model):
    highlight_id = types.Serial().field()
    user_id = types.Numeric().field().with_converter(NumericConverter)

    highlight_id_fk = ForeignKey(highlight_id, Highlight.id)
    user_id_fk = ForeignKey(user_id, User.user_id)

    primary_key = (highlight_id, user_id)
