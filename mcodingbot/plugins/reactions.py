import crescent
import hikari
import re

RUST_REGEX = re.compile(r"\brust\b", flags=re.I)

plugin = crescent.Plugin("reactions")


@plugin.include
@crescent.event
async def on_message(event: hikari.MessageCreateEvent):
    message = event.message

    if message.type == hikari.MessageType.GUILD_MEMBER_JOIN:
        await message.add_reaction("👋")
        return

    if RUST_REGEX.search(message.content) and "🚀" in message.content:
        await message.add_reaction("🚀")
        return
