import re

import crescent
from crescent.ext import tasks
import hikari

from mcodingbot.utils import Plugin
from mcodingbot.utils import Pep

plugin = Plugin()

PEP_REGEX = re.compile(r"pep[\s-]*(?P<pep>\d{1,4}\b)", re.IGNORECASE)


def get_pep(pep_number: int) -> Pep | None:
    return plugin.app.peps.get(pep_number)




@plugin.include
@crescent.command(
    name="pep", description="Find a Python Enhancement Proposal."
)
class PEPCommand:
    pep_number = crescent.option(
        int, "The PEP number.", name="pep-number", min_value=0, max_value=9999
    )
    show_embed = crescent.option(
        bool, "Whether to show the embed.", name="show-embed", default=True
    )

    async def callback(self, ctx: crescent.Context) -> None:
        if not (pep := get_pep(self.pep_number)):
            await ctx.respond(f"{self.pep_number} is not a valid pep.", ephemeral=True)
            return

        await ctx.respond(
            pep.stringify(hide_embed=not self.show_embed)
        )


@plugin.include
@crescent.event
async def on_message(event: hikari.MessageCreateEvent) -> None:
    if not event.message.content or event.author.is_bot:
        return

    pep_refs = [
        int(ref.groupdict()["pep"])
        for ref in re.finditer(PEP_REGEX, event.message.content)
    ]

    pep_refs = sorted(set(pep_refs))

    if not pep_refs:
        return

    peps = (
        get_pep(pep_number)
        for pep_number in pep_refs[:5]
    )

    pep_links_message = '\n'.join(
        pep.stringify(hide_embed=True) for pep in peps if pep
    )


    if (pep_number := len(pep_refs)) > 5:
        pep_links_message += f"\n({pep_number - 5} PEPs omitted)"

    await event.message.respond(pep_links_message, reply=True)

@plugin.include
@tasks.loop(hours=1)
async def update_peps() -> None:
    await plugin.app.peps.fetch_pep_info()
