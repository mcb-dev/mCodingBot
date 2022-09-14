from __future__ import annotations

import re
from contextlib import suppress
from datetime import datetime, timedelta, timezone

import crescent
import hikari
from cachetools import TTLCache
from crescent.ext import tasks

from mcodingbot.config import CONFIG
from mcodingbot.utils import PEPManager, Plugin

plugin = Plugin()
pep_manager = PEPManager()
MAX_AGE_FOR_SEND = timedelta(minutes=1)
recent_pep_responses: TTLCache[int, int] = TTLCache(
    maxsize=100, ttl=MAX_AGE_FOR_SEND.total_seconds() + 5
)

PEP_REGEX = re.compile(r"pep[\s-]*(?P<pep>\d{1,4}\b)", re.IGNORECASE)
DISMISS_BUTTON_ID = "dismiss"


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
@tasks.loop(hours=12)
async def update_peps() -> None:
    await pep_manager.fetch_pep_info(plugin.app)


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
        if not (pep := pep_manager.get(self.pep_number)):
            await ctx.respond(
                f"{self.pep_number} is not a valid PEP.", ephemeral=True
            )
            return

        await ctx.respond(embed=pep.embed())


def within_age_cutoff(message_created_at: datetime) -> bool:
    return datetime.now(timezone.utc) - message_created_at <= MAX_AGE_FOR_SEND


def get_peps_embed(content: str) -> hikari.Embed | None:
    pep_refs = [
        int(ref.groupdict()["pep"]) for ref in re.finditer(PEP_REGEX, content)
    ]
    peps = map(pep_manager.get, sorted(set(pep_refs))[:5])
    pep_links_message = "\n".join(str(pep) for pep in peps if pep)

    if not pep_links_message:
        return None

    embed = hikari.Embed(description=pep_links_message, color=CONFIG.theme)

    if (pep_count := len(pep_refs)) > 5:
        embed.set_footer(f"{pep_count - 5} PEPs omitted")

    return embed


@plugin.include
@crescent.event
async def on_message(event: hikari.MessageCreateEvent) -> None:
    if not event.message.content or event.author.is_bot:
        return
    if embed := get_peps_embed(event.message.content):
        response = await event.message.respond(
            embed=embed,
            component=get_dismiss_button(event.author.id),
            reply=True,
        )
        recent_pep_responses[event.message.id] = response.id


@plugin.include
@crescent.event
async def on_message_edit(event: hikari.GuildMessageUpdateEvent) -> None:
    if not event.author or event.author.is_bot:
        return

    embed = (
        get_peps_embed(event.message.content)
        if event.message.content
        else None
    )
    if original := recent_pep_responses.get(event.message.id):
        with suppress(hikari.NotFoundError):
            if embed:
                await plugin.app.rest.edit_message(
                    event.channel_id, original, embed=embed
                )
            else:
                await plugin.app.rest.delete_message(
                    event.channel_id, original
                )
                del recent_pep_responses[event.message.id]
    elif embed and within_age_cutoff(event.message.created_at):
        response = await event.message.respond(
            embed=embed,
            component=get_dismiss_button(event.author.id),
            reply=True,
        )
        recent_pep_responses[event.message.id] = response.id


@plugin.include
@crescent.event
async def on_message_delete(event: hikari.GuildMessageDeleteEvent) -> None:
    if original := recent_pep_responses.get(event.message_id):
        with suppress(hikari.NotFoundError):
            await plugin.app.rest.delete_message(event.channel_id, original)
            del recent_pep_responses[event.message_id]


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
