from __future__ import annotations
import asyncio
from collections import defaultdict
from asyncpg import UniqueViolationError

import crescent
import hikari
from mcodingbot.utils import Plugin, Context
from mcodingbot.database.models import Word, User, UserWord

plugin = Plugin()
highlights_group = crescent.Group("highlights")
highlights_cache: dict[str, list[hikari.Snowflake]] = defaultdict(list)


def _cache_highlight(word: str, *user_ids: hikari.Snowflake) -> None:
    highlights_cache[word].extend(user_ids)


def _uncache_highlight(word: str, *user_ids: hikari.Snowflake) -> None:
    for user_id in user_ids:
        highlights_cache[word].remove(user_id)
        # Deletes empty arrays from the cache
        if not highlights_cache[word]:
            del highlights_cache[word]


@plugin.include
@highlights_group.child
@crescent.command(name="create", description="Create a highlight.")
class CreateHighlight:
    word = crescent.option(str, description="The regex for the highlight.")

    async def callback(self, ctx: Context) -> None:
        if len(self.word) > 32:
            await ctx.respond(
                "Highlights can not be longer than 32 characters."
            )
            return

        word_model = await Word.get_or_create(word=self.word)
        user = await User.get_or_create(user_id=ctx.user.id)

        try:
            await word_model.users.add(user)
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
        word = await Word.exists(word=self.word)

        was_deleted = False
        if word:
            deleted_words = (
                await UserWord.delete_query()
                .where(word_id=word.id, user_id=ctx.user.id)
                .execute()
            )
            was_deleted = bool(len(deleted_words))

        if was_deleted:
            _uncache_highlight(self.word, ctx.user.id)
            await ctx.respond(f'Removed "{self.word}" from your highlights.')
            return

        await ctx.respond(f'"{self.word}" was not one of your highlights.')


@plugin.include
@highlights_group.child
@crescent.command(name="list", description="List all of your highlights.")
async def list(ctx: Context) -> None:
    user = await User.exists(user_id=ctx.user.id)

    if user is None:
        await ctx.respond("You do not have any highlights.")
        return

    words = await user.words.fetchmany()

    if not words:
        await ctx.respond("You do not have any highlights.")
        return

    await ctx.respond("\n".join(word.word for word in words))


@plugin.include
@crescent.event
async def on_start(_: hikari.StartingEvent) -> None:
    words = await Word.fetchmany()

    for word, users in zip(
        words,
        await asyncio.gather(*(word.users.fetchmany() for word in words)),
    ):
        _cache_highlight(word.word, *(user.user_id for user in users))


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
                asyncio.ensure_future(
                    _dm_user_highlight(
                        user_id=user_id,
                        highlight=highlight,
                        msg_link=event.message.make_link(event.guild_id),
                    )
                )
