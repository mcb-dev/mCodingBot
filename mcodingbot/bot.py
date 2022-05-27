import crescent

from mcodingbot.config import CONFIG


class mCB(crescent.Bot):
    def __init__(self) -> None:
        super().__init__(token=CONFIG.discord_token)
