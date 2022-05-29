import re

import crescent
import hikari

RUST_REGEX = re.compile(r"\brust\b", flags=re.I)

plugin = crescent.Plugin("reactions")


@plugin.include
@crescent.event
async def on_message(event: hikari.MessageCreateEvent) -> None:
    if event.message.type is hikari.MessageType.GUILD_MEMBER_JOIN:
        await message.add_reaction("👋")

    elif (
        event.message.content
        and RUST_REGEX.search(message.content)
        and "🚀" in message.content
    ):
        await message.add_reaction("🚀")
