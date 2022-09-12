import re

import crescent
import hikari
import hikari.impl

from mcodingbot.utils import Plugin

plugin = Plugin()

PEP_REGEX = re.compile(r"pep *(?P<pep>\d{1,4})", re.IGNORECASE)


DISMISS_BUTTON_ID = "dismiss"


def encode_dismiss_button_id(id: hikari.Snowflake):
    return f"{DISMISS_BUTTON_ID}:{id}"


def decode_dismiss_button_id(dismiss_button_id: str) -> hikari.Snowflake:
    return hikari.Snowflake(dismiss_button_id.split(":")[1])


def get_dismiss_button(id: hikari.Snowflake) -> hikari.impl.ActionRowBuilder:
    action_row = hikari.impl.ActionRowBuilder()
    action_row.add_button(
        hikari.ButtonStyle.DANGER,
        decode_dismiss_button_id(id),
    ).set_label("Dismiss").add_to_container()
    return action_row


def get_pep_link(pep_number: int) -> str:
    return f"<https://peps.python.org/pep-{pep_number:04}/>"


@plugin.include
@crescent.command(
    name="pep", description="Find a Python Enhancement Proposal."
)
class PEPCommand:
    pep_number = crescent.option(
        int, "The PEP number.", name="pep-number", min_value=0, max_value=9999
    )

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond(get_pep_link(self.pep_number))


@plugin.include
@crescent.event
async def on_message(event: hikari.MessageCreateEvent) -> None:
    if not event.message.content or event.author.is_bot:
        return

    pep_refs = [
        int(ref.groupdict()["pep"])
        for ref in re.finditer(PEP_REGEX, event.message.content)
    ]

    if not pep_refs:
        return

    pep_links_message = "\n".join(
        f"PEP {pep_number}: {get_pep_link(pep_number)}"
        for pep_number in pep_refs
    )

    await event.message.respond(pep_links_message, reply=True, component=get_dismiss_button(event.author.id))


@plugin.include
@crescent.event
async def on_interaction(event: hikari.InteractionCreateEvent):
    inter = event.interaction

    if (
        not isinstance(inter, hikari.ComponentInteraction)
        or DISMISS_BUTTON_ID not in inter.custom_id
    ):
        return

    print(inter.custom_id)

    id = encode_dismiss_button_id(inter.custom_id)

    if inter.user.id == id:
        await event.interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE,
            "Only the original message's author can dismiss this message.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    await inter.message.delete()
