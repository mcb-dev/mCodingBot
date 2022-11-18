from __future__ import annotations

import logging
from dataclasses import dataclass
from math import log2
from typing import TYPE_CHECKING, Any

from crescent.ext import tasks

from mcodingbot.config import CONFIG
from mcodingbot.utils import Plugin

if TYPE_CHECKING:
    from mcodingbot.bot import Bot


LOGGER = logging.getLogger(__file__)


plugin = Plugin()


@plugin.include
@tasks.loop(minutes=5)
async def loop() -> None:
    try:
        await update_channels(plugin.app)
    except Exception:
        LOGGER.error("Failed to update channel stats:", exc_info=True)


async def update_channels(bot: Bot) -> None:
    if not CONFIG.mcoding_server:
        return

    assert (
        CONFIG.sub_count_channel
    ), "sub count channel id for mcoding server expected."
    assert (
        CONFIG.view_count_channel
    ), "view count channel id for mcoding server expected."
    assert (
        CONFIG.member_count_channel
    ), "member count channel id for mcoding server expected."

    stats = await get_stats(bot)

    sub_channel = bot.cache.get_guild_channel(CONFIG.sub_count_channel)
    view_channel = bot.cache.get_guild_channel(CONFIG.view_count_channel)
    member_channel = bot.cache.get_guild_channel(CONFIG.member_count_channel)

    if sub_channel:
        await sub_channel.edit(name=f"Subs: {display_stats(stats.subs)}")
    else:
        LOGGER.warning("No sub count channel to update stats for.")

    if view_channel:
        await view_channel.edit(name=f"Views: {display_stats(stats.views)}")
    else:
        LOGGER.warning("No view count channel to update stats for.")

    if not member_channel:
        return LOGGER.warning("No member count channel to update stats for.")

    guild = bot.cache.get_guild(CONFIG.mcoding_server)
    if not guild:
        return LOGGER.warning(
            "Couldn't find mCoding guild, not updating member count."
        )
    guild_approx_members = guild.member_count
    if guild_approx_members is None:
        return LOGGER.warning("Cached guild has no aproximate member count.")
    cached_members = len(bot.cache.get_members_view_for_guild(guild.id))

    # at startup, cached_members will be very small because it relies on
    # the guild being chuncked, which happens *after* startup. We can't
    # just rely on the aproximate_member_count though, because that is
    # never updated after the bot first starts.
    member_count = max(guild_approx_members, cached_members)

    await member_channel.edit(name=f"Members: {display_stats(member_count)}")


@dataclass
class Stats:
    subs: float
    views: float


BASE_URL = "https://www.googleapis.com/youtube/v3/channels"
_last_known_stats = Stats(0, 0)


async def get_stats(bot: Bot) -> Stats:
    link = (
        f"{BASE_URL}?part=statistics&id={CONFIG.mcoding_yt_id}"
        f"&key={CONFIG.yt_api_key}"
    )

    async with bot.session.get(link) as res:
        res.raise_for_status()
        response: dict[str, Any] = await res.json()

    if not response:
        LOGGER.error("Received 2XX but no data.")
        return _last_known_stats

    items = response.get("items")
    if not items:
        LOGGER.error("Response did not contain 'items'.")
        return _last_known_stats

    channel = items[0]
    if channel.get("id") != CONFIG.mcoding_yt_id:
        LOGGER.error("Channel ID was not mCoding.")
        return _last_known_stats

    statistics = channel.get("statistics")
    if not statistics:
        LOGGER.error("mCoding channel did not contain 'statistics'.")
        return _last_known_stats

    subs = float(statistics.get("subscriberCount", 0))
    views = float(statistics.get("viewCount", 0))

    if not (subs and views):
        LOGGER.error(
            "Statistics did not contain subscriberCount and viewCount."
        )
        return _last_known_stats

    _last_known_stats.subs = subs
    _last_known_stats.views = views
    return _last_known_stats


def strip_trailing_zeros(n: int | float) -> int | float:
    if float(n).is_integer():
        return int(n)
    return n


def truncate_decimals(number: int | float, ndigits: int = 0) -> float:
    n: int | float = 10**ndigits
    return int(number * n) / n


def display_stats(stat: int | float) -> str:
    if stat < 1_000:
        pretty_stat = stat
        unit = ""
    elif stat < 1_000_000:
        pretty_stat = stat / 1_000
        unit = "K"
    else:
        pretty_stat = stat / 1_000_000
        unit = "M"

    pretty_stat = strip_trailing_zeros(truncate_decimals(pretty_stat, 2))
    exp_stat = strip_trailing_zeros(truncate_decimals(log2(stat), 2))
    # ^ this might not be as accurate as the member count thing when
    # someone picky actually calculates it, but I suppose it's not
    # gonna be such a problem if it's gonna be shown as e.g. "44.3K"

    return f"2**{exp_stat} ({pretty_stat}{unit})"
