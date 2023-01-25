import crescent
import hikari

from mcodingbot.config import CONFIG
from mcodingbot.model import Model

bot = hikari.GatewayBot(
    token=CONFIG.discord_token,
    intents=(
        hikari.Intents.ALL_UNPRIVILEGED
        | hikari.Intents.GUILD_MEMBERS
        | hikari.Intents.MESSAGE_CONTENT
    ),
)

model = Model()
client = crescent.Client(bot, model)
client.plugins.load_folder("mcodingbot.plugins")

bot.event_manager.subscribe(hikari.StartedEvent, model.on_start)
bot.event_manager.subscribe(hikari.StoppedEvent, model.on_stop)

bot.run()
