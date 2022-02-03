#  MIT License
#
#  Copyright (c) [2022] [GozZzer]
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import asyncpg
import hikari
from hikari import Snowflake, VoiceState
from hikari.api import CacheView

from clanwars.database.utils.clan_utils import get_clan_member, get_clan_name

CHANNELS_LIST = [894316552084672572, 894316856326881324,
                 934571700794818590, 934571740607160372,
                 894322356242251806, 894322374256783420]
CHANNELS = {
    "1": {
        "category": 934571640707219496,
        "team1": 934571700794818590,
        "team2": 934571740607160372
    },
    "3": {
        "category": 894314932953288755,
        "team1": 894316552084672572,
        "team2": 894316856326881324
    },
    "4": {
        "category": 894321542828269678,
        "team1": 894322356242251806,
        "team2": 894322374256783420
    }
}


async def check_start(
        event: hikari.events.voice_events.VoiceStateUpdateEvent,
        cache: hikari.api.Cache,
        pool: asyncpg.pool.Pool) -> ((str, hikari.channels.GuildVoiceChannel, CacheView[Snowflake, VoiceState]),
                                     (str, hikari.channels.GuildVoiceChannel, CacheView[Snowflake, VoiceState])):
    guild = await event.app.rest.fetch_guild(event.state.guild_id)
    # check if channel is clanwar channel
    if (event.state.channel_id | event.old_state.channel_id) not in CHANNELS_LIST:
        return
    channel_id = event.state.channel_id if event.state.channel_id else event.old_state.channel_id
    channel = hikari.channels.GuildChannel = guild.get_channel(channel_id)
    category: hikari.channels.GuildCategory = guild.get_channel(channel.parent_id)
    channel_1: hikari.channels.GuildVoiceChannel = guild.get_channel(CHANNELS[[str(key) for key in CHANNELS if CHANNELS[key]['category'] == category.id][0]]["team1"])
    channel_2: hikari.channels.GuildVoiceChannel = guild.get_channel(CHANNELS[[str(key) for key in CHANNELS if CHANNELS[key]['category'] == category.id][0]]["team2"])
    members_channel_1 = cache.get_voice_states_view_for_channel(guild, channel_1)
    members_channel_2 = cache.get_voice_states_view_for_channel(guild, channel_2)
    # check if channels are full
    if len(members_channel_1) & len(members_channel_2) != channel_1.user_limit:
        return
    # check name of the clan_1
    clan_name_1 = None
    for member in members_channel_1:
        if clan_name_1 is None:
            clan_name_1 = await get_clan_name(pool, member)
            continue
        if await get_clan_name(pool, member) != clan_name_1:
            return
    # check name of the clan_"
    clan_name_2 = None
    for member in members_channel_2:
        if clan_name_2 is None:
            clan_name_2 = await get_clan_name(pool, member)
            continue
        if await get_clan_name(pool, member) != clan_name_2:
            return

    return (clan_name_1, channel_1, members_channel_1), (clan_name_2, channel_2, members_channel_2)




