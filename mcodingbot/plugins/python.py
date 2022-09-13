import re

import crescent
import hikari
from crescent.ext import tasks

from mcodingbot.config import CONFIG
from mcodingbot.utils import PepManager, Plugin

plugin = Plugin()

PEP_REGEX = re.compile(r"pep[\s-]*(?P<pep>\d{1,4}\b)", re.IGNORECASE)
DISMISS_BUTTON_ID = "dismiss"
PEP_MANAGER = PepManager()


def encode_dismiss_button_id(id: hikari.Snowflake) -> str:
    return f"{DISMISS_BUTTON_ID}:{id}"


def decode_dismiss_button_id(dismiss_button_id: str) -> hikari.Snowflake:
    return hikari.Snowflake(dismiss_button_id.split(":")[1])


def get_dismiss_button(id: hikari.Snowflake) -> hikari.api.ActionRowBuilder:
    action_row = plugin.app.rest.build_action_row()
    action_row.add_button(
        hikari.ButtonStyle.SECONDARY, encode_dismiss_button_id(id)
    ).set_label("Dismiss").add_to_container()
    return action_row


@plugin.include
@tasks.loop(hours=1)
async def update_peps() -> None:
    await PEP_MANAGER.fetch_pep_info(plugin.app)


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
        if not (pep := PEP_MANAGER.get(self.pep_number)):
            await ctx.respond(
                f"{self.pep_number} is not a valid pep.", ephemeral=True
            )
            return

        await ctx.respond(embed=pep.embed())


@plugin.include
@crescent.event
async def on_message(event: hikari.MessageCreateEvent) -> None:
    if not event.message.content or event.author.is_bot:
        return

    pep_refs = [
        int(ref.groupdict()["pep"])
        for ref in re.finditer(PEP_REGEX, event.message.content)
    ]

    peps = map(PEP_MANAGER.get, sorted(set(pep_refs))[:5])
    pep_links_message = "\n".join(str(pep) for pep in peps if pep)

    if not pep_links_message:
        return

    embed = hikari.Embed(description=pep_links_message, color=CONFIG.theme)

    if (pep_number := len(pep_refs)) > 5:
        embed.set_footer(f"{pep_number - 5} PEPs omitted")

    await event.message.respond(
        embed=embed, component=get_dismiss_button(event.author.id), reply=True
    )


@plugin.include
@crescent.event
async def on_interaction(event: hikari.InteractionCreateEvent) -> None:
    inter = event.interaction

    if not (
        isinstance(inter, hikari.ComponentInteraction)
        and DISMISS_BUTTON_ID in inter.custom_id
    ):
        return

    if inter.user.id != decode_dismiss_button_id(inter.custom_id):
        await inter.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE,
            "Only the person who triggered this message can dismiss it.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    await inter.message.delete()
