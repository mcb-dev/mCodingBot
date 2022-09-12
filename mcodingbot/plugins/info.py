import crescent
import hikari

from mcodingbot.config import CONFIG
from mcodingbot.utils import Plugin

plugin = Plugin()


@plugin.include
@crescent.command(name="ping", description="Pong!")
class PingCommand:
    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond(f"Pong! {round(ctx.app.heartbeat_latency*1000)} ms.")


@plugin.include
@crescent.command(name="links", description="Useful links")
class LinksCommand:
    async def callback(self, ctx: crescent.Context) -> None:
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
@crescent.command(name="pep", description="Find a Python Enhancement Proposal")
class PEPCommand:
    pep_number = crescent.option(int, "the PEP number")

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond(f"https://peps.python.org/pep-{self.pep_number:03}/")
