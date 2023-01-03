from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import NamedTuple

import crescent
import hikari
from asyncpg import UniqueViolationError
from floodgate import FixedMapping

from mcodingbot.config import CONFIG
from mcodingbot.database.models import Highlight, User, UserHighlight
from mcodingbot.utils import Context, Plugin

MAX_HIGHLIGHTS = 25
MAX_HIGHLIGHT_LENGTH = 32


class SentMessageBucket(NamedTuple):
    user: int
    channel: int


class TriggerBucket(NamedTuple):
    channel: int
    highlight: str


plugin = Plugin()
highlights_group = crescent.Group("highlights")
highlights_cache: dict[str, list[hikari.Snowflake]] = defaultdict(list)
sent_message_cooldown: FixedMapping[SentMessageBucket] = FixedMapping(
    *CONFIG.highlight_message_sent_cooldown
)
trigger_cooldown: FixedMapping[TriggerBucket] = FixedMapping(
    *CONFIG.highlight_trigger_cooldown
)


def _cache_highlight(highlight: str, *user_ids: hikari.Snowflake) -> None:
    highlights_cache[highlight].extend(user_ids)


def _uncache_highlight(highlight: str, *user_ids: hikari.Snowflake) -> None:
    for user_id in user_ids:
        highlights_cache[highlight].remove(user_id)
        # Deletes empty arrays from the cache
        if not highlights_cache[highlight]:
            del highlights_cache[highlight]


@plugin.include
@highlights_group.child
@crescent.command(name="create", description="Create a highlight.")
class CreateHighlight:
    word = crescent.option(str, description="The regex for the highlight.")

    async def callback(self, ctx: Context) -> None:
        if len(self.word) > MAX_HIGHLIGHT_LENGTH:
            await ctx.respond(
                "Highlights can not be longer than 32 characters.",
                ephemeral=True,
            )
            return

        total_highlights = await UserHighlight.count(user_id=ctx.user.id)
        if total_highlights >= MAX_HIGHLIGHTS:
            await ctx.respond(
                f"You can only have {MAX_HIGHLIGHTS} highlights.",
                ephemeral=True,
            )
            return

        highlight_model = await Highlight.get_or_create(highlight=self.word)
        user = await User.get_or_create(user_id=ctx.user.id)

        try:
            await highlight_model.users.add(user)
        except UniqueViolationError:
            await ctx.respond(
                f'"{self.word}" is already one of your highlights.',
                ephemeral=True,
            )
        else:
            await ctx.respond(
                f'Added "{self.word}" to your highlights.', ephemeral=True
            )
            _cache_highlight(self.word, ctx.user.id)


@plugin.include
@highlights_group.child
@crescent.command(name="delete", description="Delete a highlight.")
class DeleteHighlight:
    word = crescent.option(str, "The regex for the highlight.")

    async def callback(self, ctx: Context) -> None:
        highlight = await Highlight.exists(highlight=self.word)

        was_deleted = False
        if highlight:
            deleted_highlights = (
                await UserHighlight.delete_query()
                .where(highlight_id=highlight.id, user_id=ctx.user.id)
                .execute()
            )
            was_deleted = bool(len(deleted_highlights))

        if was_deleted:
            _uncache_highlight(self.word, ctx.user.id)
            await ctx.respond(
                f'Removed "{self.word}" from your highlights.', ephemeral=True
            )
            return

        await ctx.respond(
            f'"{self.word}" was not one of your highlights.', ephemeral=True
        )


@plugin.include
@highlights_group.child
@crescent.command(name="list", description="List all of your highlights.")
async def list_highlights(ctx: Context) -> None:
    user = await User.exists(user_id=ctx.user.id)

    if user is None:
        await ctx.respond("You do not have any highlights.", ephemeral=True)
        return

    highlights = await user.highlights.fetchmany()

    if not highlights:
        await ctx.respond("You do not have any highlights.", ephemeral=True)
        return

    embed = hikari.Embed(
        title="Your Highlights",
        description="\n".join(hl.highlight for hl in highlights),
        color=CONFIG.theme,
    )
    await ctx.respond(embed=embed, ephemeral=True)


@plugin.include
@crescent.event
async def on_start(_: hikari.StartingEvent) -> None:
    if CONFIG.no_db_mode:
        return

    highlights = await Highlight.fetchmany()

    for highlight, user_highlights in zip(
        highlights,
        await asyncio.gather(
            *(
                UserHighlight.fetchmany(highlight_id=highlight.id)
                for highlight in highlights
            )
        ),
    ):
        _cache_highlight(
            highlight.highlight,
            *(user_highlight.user_id for user_highlight in user_highlights),
        )


async def _dm_user_highlight(
    triggering_message: hikari.Message, triggers: list[str], user_id: int
) -> None:
    _avatar_url = triggering_message.author.avatar_url
    avatar_url = _avatar_url.url if _avatar_url else None
    embed = (
        hikari.Embed(
            title="Highlight Triggered",
            url=triggering_message.make_link(CONFIG.mcoding_server),
            description=triggering_message.content,
            color=CONFIG.theme,
        )
        .set_footer(f"Highlight(s): {', '.join(triggers)}")
        .set_author(name=triggering_message.author.username, icon=avatar_url)
    )
    channel = await plugin.app.rest.create_dm_channel(user_id)
    await channel.send(embed=embed)


@plugin.include
@crescent.event
async def on_message(event: hikari.GuildMessageCreateEvent) -> None:
    if event.is_bot:
        return

    message_bucket = SentMessageBucket(
        user=event.author_id, channel=event.channel_id
    )
    sent_message_cooldown.reset(message_bucket)
    sent_message_cooldown.trigger(message_bucket)

    if not event.content:
        return

    highlights: defaultdict[hikari.Snowflake, list[str]] = defaultdict(list)

    for highlight, users in highlights_cache.items():
        if highlight in event.content:
            retry_after = trigger_cooldown.trigger(
                TriggerBucket(channel=event.channel_id, highlight=highlight)
            )
            if retry_after:
                # this highlight has been triggered in this channel too
                # many times, so it's on cooldown.
                continue

            for user_id in users:
                if user_id == event.author.id:
                    continue
                highlights[user_id].append(highlight)

    for user_id, hls in highlights.items():
        if not sent_message_cooldown.can_trigger(
            SentMessageBucket(user=user_id, channel=event.channel_id)
        ):
            # the user has sent messages in this channel, so highlights are
            # not active for them in this channel.
            continue
        asyncio.ensure_future(
            _dm_user_highlight(
                triggering_message=event.message, triggers=hls, user_id=user_id
            )
        )
