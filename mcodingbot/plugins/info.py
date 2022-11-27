from __future__ import annotations

import crescent
import hikari

from mcodingbot.config import CONFIG
from mcodingbot.utils import Context, Plugin
from mcodingbot.plugins import stats

plugin = Plugin()


@plugin.include
@crescent.command(name="ping", description="Pong!")
async def ping(ctx: Context) -> None:
    await ctx.respond(f"Pong! {round(ctx.app.heartbeat_latency*1000)} ms.")


@plugin.include
@crescent.command(name="links", description="Useful links")
async def links(ctx: Context) -> None:
    embed = hikari.Embed(
        title="Links",
        color=CONFIG.theme,
        description=(
            f"**[mCoding Youtube]({CONFIG.mcoding_youtube})**\n"
            f"**[mCoding repo]({CONFIG.mcoding_repo})**\n"
            f"**[mCodingBot repo]({CONFIG.mcodingbot_repo})**"
        ),
    )
    await ctx.respond(embed=embed)

@plugin.include
@crescent.command(name="stats", description="Exact values for mCoding statistics")
async def stats(ctx: Context) -> None:
    stats = await stats.get_stats(ctx.session.bot)
    embed = hikari.Embed(
        title="mCoding stats",
        color=CONFIG.theme,
        description=(
            f"Server members: `{ctx.server.member_count:,}`\n"
            f"Subscribers: `{stats.subs:,}`\n"
            f"Views: {stats.views:,}"
        ),
    )
    await ctx.respond(embed=embed)

