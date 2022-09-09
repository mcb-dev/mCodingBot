import re

import crescent
import hikari

from mcodingbot.utils import Plugin

RUST_REGEX = re.compile(r"(\brust\b|\bblazingly\s+fast\b)", flags=re.I)

plugin = Plugin()


@plugin.include
@crescent.event
async def on_message(event: hikari.MessageCreateEvent) -> None:
    for add_reaction in reaction_checks:
        if add_reaction(event):
            break
    
def reaction_welcome(event: hikari.MessageCreateEvent) -> bool:
    if event.message.type is hikari.MessageType.GUILD_MEMBER_JOIN:
        await event.message.add_reaction("👋")
        return True
    return False

def reaction_rust(event: hikari.MessageCreateEvent) -> bool:
    if (
        event.message.content
        and RUST_REGEX.search(event.message.content)
        and "🚀" in event.message.content
    ):
        await event.message.add_reaction("🚀")
        return True
    return False

reaction_checks: tuple[Callable] = (reaction_welcome, reaction_rust)