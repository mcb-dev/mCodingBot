from __future__ import annotations

import hikari
import crescent

from mcodingbot.config import CONFIG

plugin = crescent.Plugin()


@plugin.include
@crescent.command(
    name="restart",
    description="Restarts the bot.",
    default_member_permissions=hikari.Permissions.MODERATE_MEMBERS,
    dm_enabled=False,
    guild=CONFIG.mcoding_server,
)
class RestartBot:
    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond("Restarting bot...")
        await ctx.app.close()
