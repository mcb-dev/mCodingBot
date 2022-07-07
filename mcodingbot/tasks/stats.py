from __future__ import annotations

import asyncio
import traceback
from dataclasses import dataclass
from math import log
from typing import TYPE_CHECKING, Any

from mcodingbot.config import CONFIG

if TYPE_CHECKING:
    from mcodingbot.bot import Bot


async def loop_update_channels(bot: Bot) -> None:
    while True:
        try:
            await update_channels(bot)
        except Exception:
            print("Failed to update channel stats:")
            traceback.print_exc()

        await asyncio.sleep(5 * 60)


async def update_channels(bot: Bot) -> None:
    stats = await get_stats(bot)

    sub_channel = bot.cache.get_guild_channel(CONFIG.sub_count_channel)
    view_channel = bot.cache.get_guild_channel(CONFIG.view_count_channel)
    member_channel = bot.cache.get_guild_channel(CONFIG.member_count_channel)

    assert sub_channel
    assert view_channel
    assert member_channel

    await sub_channel.edit(name=f"Subs: {display_stats(stats.subs)}")
    await view_channel.edit(name=f"Views: {display_stats(stats.views)}")

    guild = bot.cache.get_guild(CONFIG.mcoding_server)
    assert guild
    member_count = guild.member_count
    assert member_count is not None

    await member_channel.edit(name=f"Members: {display_stats(member_count)}")


@dataclass
class Stats:
    subs: float
    views: float


BASE_URL = "https://www.googleapis.com/youtube/v3/channels"
LAST_STATS = Stats(0, 0)


async def get_stats(bot: Bot) -> Stats:
    link = (
        f"{BASE_URL}?part=statistics&id={CONFIG.mcoding_yt_id}"
        f"&key={CONFIG.yt_api_key}"
    )

    session = await bot.get_session()
    async with session.get(link) as res:
        response: dict[str, Any] = await res.json()

    if not response:
        return LAST_STATS

    items = response.get("items")
    if not items:
        return LAST_STATS

    channel = items[0]
    if channel.get("id") != CONFIG.mcoding_yt_id:
        return LAST_STATS

    statistics = channel.get("statistics")
    if not statistics:
        return LAST_STATS

    subs = float(statistics.get("subscriberCount", 0))
    views = float(statistics.get("viewCount", 0))

    if not subs or not views:
        return LAST_STATS

    LAST_STATS.subs = subs
    LAST_STATS.views = views
    return LAST_STATS


def display_stats(stat: int | float) -> str:
    int_stat = stat

    if int_stat < 10**3:
        pretty_stat = int_stat
        unit = ""
    elif int_stat < 10**6:
        pretty_stat = int_stat / 10**3
        unit = "K"
    else:
        pretty_stat = int_stat / 10**6
        unit = "M"

    pretty_stat = round(pretty_stat, 2)

    exp_stat = round(log(int_stat, 2), 1)
    # ^ this might not be as accurate as the member count thing when
    # someone picky actually calculates it, but I suppose it's not
    # gonna be such a problem if it's gonna be shown as e.g. "44.3K"

    if exp_stat % 1 == 0:
        exp_stat = int(exp_stat)

    if pretty_stat % 1 == 0:
        pretty_stat = int(pretty_stat)

    return f"2**{exp_stat} ({pretty_stat}{unit})"
