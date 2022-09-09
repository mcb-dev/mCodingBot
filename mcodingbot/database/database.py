from __future__ import annotations

import apgorm

from mcodingbot.database.models.user import User


class Database(apgorm.Database):
    users = User
