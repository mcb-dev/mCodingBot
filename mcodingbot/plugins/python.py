import re

import crescent
import hikari

from mcodingbot.utils import Plugin

plugin = Plugin()

PEP_REGEX = re.compile(r"pep[\s-]*(?P<pep>\d{1,4}\b)", re.IGNORECASE)


def get_pep_link(pep_number: int, *, hide_embed: bool) -> str:
    url = f"https://peps.python.org/pep-{pep_number:04}/"
    return f"<{url}>" if hide_embed else url


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
        await ctx.respond(
            get_pep_link(self.pep_number, hide_embed=not self.show_embed)
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

    pep_links_message = "\n".join(
        f"PEP {pep_number}: {get_pep_link(pep_number, hide_embed=True)}"
        for pep_number in pep_refs[:5]
    )

    if (peps := len(pep_refs)) > 5:
        pep_links_message += f"\n({peps - 5} PEPs omitted)"

    await event.message.respond(pep_links_message, reply=True)
