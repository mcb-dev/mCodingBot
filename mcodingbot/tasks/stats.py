from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from math import log
from typing import TYPE_CHECKING, Any

from mcodingbot.config import CONFIG

if TYPE_CHECKING:
    from mcodingbot.bot import Bot


LOGGER = logging.getLogger(__file__)


async def loop_update_channels(bot: Bot) -> None:
    while True:
        try:
            await update_channels(bot)
        except Exception:
            LOGGER.error("Failed to update channel stats:", exc_info=True)

        await asyncio.sleep(5 * 60)


async def update_channels(bot: Bot) -> None:
    stats = await get_stats(bot)

    sub_channel = bot.cache.get_guild_channel(CONFIG.sub_count_channel)
    view_channel = bot.cache.get_guild_channel(CONFIG.view_count_channel)
    member_channel = bot.cache.get_guild_channel(CONFIG.member_count_channel)

    assert sub_channel
    assert view_channel
    assert member_channel

    if sub_channel:
        await sub_channel.edit(name=f"Subs: {display_stats(stats.subs)}")
    else:
        LOGGER.warning("No sub count channel to update stats for.")

    if view_channel:
        await view_channel.edit(name=f"Views: {display_stats(stats.views)}")
    else:
        LOGGER.warning("No view count channel to update stats for.")

    guild = bot.cache.get_guild(CONFIG.mcoding_server)
    if not guild:
        return LOGGER.warning(
            "Couldn't find mCoding guild, not updating member count."
        )

    member_count = guild.member_count
    if member_count is None:
        return LOGGER.error("Cached guild didn't contain member count.")

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

    session = await bot.get_session()
    async with session.get(link) as res:
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


def display_stats(stat: int | float) -> str:
    if stat < 10**3:
        pretty_stat = stat
        unit = ""
    elif stat < 10**6:
        pretty_stat = stat / 10**3
        unit = "K"
    else:
        pretty_stat = stat / 10**6
        unit = "M"

    pretty_stat = round(pretty_stat, 2)

    exp_stat = round(log(stat, 2), 1)
    # ^ this might not be as accurate as the member count thing when
    # someone picky actually calculates it, but I suppose it's not
    # gonna be such a problem if it's gonna be shown as e.g. "44.3K"

    if exp_stat.is_integer():
        exp_stat = int(exp_stat)

    if pretty_stat.is_integer():
        pretty_stat = int(pretty_stat)

    return f"2**{exp_stat} ({pretty_stat}{unit})"
