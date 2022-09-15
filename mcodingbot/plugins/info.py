import crescent
import hikari

from mcodingbot.config import CONFIG
from mcodingbot.utils import Context, Plugin

plugin = Plugin()


def nat_round(__x: int | float) -> int:
    n = int(__x)
    return n + (__x - n >= 0.5)


@plugin.include
@crescent.command(name="ping", description="Pong!")
async def ping(ctx: Context) -> None:
    await ctx.respond(f"Pong! {nat_round(ctx.app.heartbeat_latency*1000)} ms.")


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
