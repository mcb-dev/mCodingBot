import re

import crescent
import hikari

from mcodingbot.utils import Plugin

plugin = Plugin()

pep_regex = re.compile(r"pep *\d{1,4}", re.IGNORECASE)


def extract_pep_number(ref: str) -> int:
    return int(ref.casefold().removeprefix("pep").strip())


def get_pep_link(pep_number: int) -> str:
    return f"<https://peps.python.org/pep-{pep_number:04}/>"


@plugin.include
@crescent.command(name="pep", description="Find a Python Enhancement Proposal")
class PEPCommand:
    pep_number = crescent.option(int, "the PEP number")

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond(get_pep_link(self.pep_number))


@plugin.include
@crescent.event
async def on_message(event: hikari.MessageCreateEvent) -> None:
    if event.message.content is not None:
        pep_refs = [
            extract_pep_number(ref.group())
            for ref in re.finditer(pep_regex, event.message.content)
        ]

        if not pep_refs:
            return

        pep_links_message = "\n".join(
            [
                f"PEP {pep_number}: {pep_link}"
                for pep_number, pep_link in zip(
                    pep_refs, map(get_pep_link, pep_refs)
                )
            ]
        )

        await event.message.respond(pep_links_message)
