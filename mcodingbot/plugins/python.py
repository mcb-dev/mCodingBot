import crescent

from mcodingbot.utils import Plugin

plugin = Plugin()


@plugin.include
@crescent.command(name="pep", description="Find a Python Enhancement Proposal")
class PEPCommand:
    pep_number = crescent.option(int, "the PEP number")

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond(f"https://peps.python.org/pep-{self.pep_number:03}/")
