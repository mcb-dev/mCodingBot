from __future__ import annotations

import crescent
import hikari

from mcodingbot.config import CONFIG
from mcodingbot.utils import Context, Plugin

plugin = Plugin()


@plugin.include
@crescent.command(
    name="restart",
    description="Restarts the bot.",
    default_member_permissions=hikari.Permissions.ADMINISTRATOR,
    dm_enabled=False,
    guild=CONFIG.mcoding_server,
)
async def restart(ctx: Context) -> None:
    await ctx.respond("Restarting bot...")
    await ctx.app.close()
