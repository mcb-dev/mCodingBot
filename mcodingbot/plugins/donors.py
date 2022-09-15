from __future__ import annotations

import asyncio

import crescent
import hikari
from crescent.ext import tasks

from mcodingbot.config import CONFIG
from mcodingbot.database.models.user import User
from mcodingbot.utils import Context, Plugin

plugin = Plugin()


@plugin.include
@crescent.command(
    name="set-donor-status",
    description="Sets the donor status for a user.",
    default_member_permissions=hikari.Permissions.MANAGE_ROLES,
    dm_enabled=False,
)
class SetDonorStatus:
    member = crescent.option(
        hikari.User, "The member to set the donor status for."
    )
    is_donor = crescent.option(
        bool, "Whether or not this user is a donor.", name="is-donor"
    )

    async def callback(self, ctx: Context) -> None:
        assert ctx.guild_id

        await _update_donor_role(self.member.id, self.is_donor)

        await ctx.respond(
            f"{self.member.mention} {'' if self.is_donor else 'un'}marked"
            " as a donor.",
            ephemeral=True,
        )


@plugin.include
@crescent.event
async def on_member_update(event: hikari.MemberUpdateEvent) -> None:
    await _give_donor_role_if_donor(event.member)


@plugin.include
@tasks.loop(hours=1)
async def add_donor_role() -> None:
    role_add_tasks: list[asyncio.Task[None]] = []
    for member in plugin.app.cache.get_members_view_for_guild(
        CONFIG.mcoding_server
    ).values():
        role_add_tasks.append(
            asyncio.create_task(_give_donor_role_if_donor(member))
        )

    await asyncio.gather(*role_add_tasks)


async def _give_donor_role_if_donor(member: hikari.Member) -> None:
    if await _is_donor(member):
        await _update_donor_role(member.id, is_donor=True)


async def _is_donor(member: hikari.Member) -> bool:
    if (
        CONFIG.patron_role in member.role_ids
        or CONFIG.donor_role in member.role_ids
    ):
        return True

    if CONFIG.no_db_mode:
        user = None
    else:
        user = await User.exists(user_id=member.id)
    return user.is_donor if user else False


async def _update_donor_role(
    member: int | hikari.Member, is_donor: bool
) -> None:
    user_id = int(member)
    user = await User.get_or_create(user_id)
    user.is_donor = is_donor
    await user.save()

    if (
        isinstance(member, hikari.Member)
        and CONFIG.donor_role in member.role_ids
    ):
        return

    if is_donor:
        await plugin.app.rest.add_role_to_member(
            CONFIG.mcoding_server, user_id, CONFIG.donor_role
        )
    else:
        await plugin.app.rest.remove_role_from_member(
            CONFIG.mcoding_server, user_id, CONFIG.donor_role
        )
