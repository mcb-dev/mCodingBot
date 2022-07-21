import re

import crescent
import hikari

from mcodingbot.utils import Plugin

RUST_REGEX = re.compile(r"\brust\b", flags=re.I)

plugin = Plugin()


@plugin.include
@crescent.event
async def on_message(event: hikari.MessageCreateEvent) -> None:
    if event.message.type is hikari.MessageType.GUILD_MEMBER_JOIN:
        await event.message.add_reaction("👋")

    elif (
        event.message.content
        and RUST_REGEX.search(event.message.content)
        and "🚀" in event.message.content
    ):
        await event.message.add_reaction("🚀")
