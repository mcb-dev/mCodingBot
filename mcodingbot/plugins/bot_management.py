from __future__ import annotations

import crescent
import hikari

from mcodingbot.config import CONFIG
from mcodingbot.utils import Plugin, Context

plugin = Plugin()


@plugin.include
@crescent.command(
    name="restart",
    description="Restarts the bot.",
    default_member_permissions=hikari.Permissions.ADMINISTRATOR,
    dm_enabled=False,
    guild=CONFIG.mcoding_server,
)
class RestartBot:
    async def callback(self, ctx: Context) -> None:
        await ctx.respond("Restarting bot...")
        await ctx.app.close()
