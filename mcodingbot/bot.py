import crescent

from mcodingbot.config import CONFIG


class Bot(crescent.Bot):
    def __init__(self) -> None:
        super().__init__(token=CONFIG.discord_token)

        self.plugins.load("mcodingbot.plugins.basic")
        self.plugins.load("mcodingbot.plugins.reactions")
