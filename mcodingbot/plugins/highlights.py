from __future__ import annotations

import asyncio
from collections import defaultdict

import crescent
import hikari
from asyncpg import UniqueViolationError

from mcodingbot.database.models import Highlight, User, UserHighlight
from mcodingbot.utils import Context, Plugin

MAX_HIGHLIGHTS = 25
MAX_HIGHLIGHT_LENGTH = 32

plugin = Plugin()
highlights_group = crescent.Group("highlights")
highlights_cache: dict[str, list[hikari.Snowflake]] = defaultdict(list)


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
            await ctx.respond(f'Added "{self.word}" to your highlights.')
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
            await ctx.respond(f'Removed "{self.word}" from your highlights.')
            return

        await ctx.respond(
            f'"{self.word}" was not one of your highlights.', ephemeral=True
        )


@plugin.include
@highlights_group.child
@crescent.command(name="list", description="List all of your highlights.")
async def list(ctx: Context) -> None:
    user = await User.exists(user_id=ctx.user.id)

    if user is None:
        await ctx.respond("You do not have any highlights.")
        return

    highlights = await user.highlights.fetchmany()

    if not highlights:
        await ctx.respond("You do not have any highlights.")
        return

    await ctx.respond(
        "\n".join(highlight.highlight for highlight in highlights)
    )


@plugin.include
@crescent.event
async def on_start(_: hikari.StartingEvent) -> None:
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
    user_id: hikari.Snowflake, highlight: str, msg_link: str
) -> None:
    channel = await plugin.app.rest.create_dm_channel(user_id)
    await channel.send(f"Highlight found: {highlight}\n{msg_link}")


@plugin.include
@crescent.event
async def on_message(event: hikari.GuildMessageCreateEvent) -> None:
    if not event.content or event.is_bot:
        return

    for highlight, users in highlights_cache.items():
        if highlight in event.content.split():
            for user_id in users:
                if user_id == event.author.id:
                    continue
                asyncio.ensure_future(
                    _dm_user_highlight(
                        user_id=user_id,
                        highlight=highlight,
                        msg_link=event.message.make_link(event.guild_id),
                    )
                )
