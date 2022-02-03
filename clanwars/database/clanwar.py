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

from clanwars.database.utils.games_utils import set_category_game, new_game, set_channels_game, set_clans_game, set_clan_members_game
from clanwars.database.utils.seasons_utils import get_current_season


async def start_game(
        pool: asyncpg.pool.Pool,
        guild: hikari.RESTGuild,
        member_clan_1, member_clan_2,
        clan_name_1, clan_name_2):
    season = await get_current_season(pool)
    game_id = await new_game(pool, season)
    category: hikari.channels.GuildCategory = await guild.create_category(f"Game# {game_id}")
    await set_category_game(pool, season, game_id, category.id)
    text_channel = await guild.create_text_channel(f"Game#{game_id}", category=category)
    voice_channel_1 = await guild.create_voice_channel(clan_name_1, category=category)
    voice_channel_2 = await guild.create_voice_channel(clan_name_2, category=category)
    await set_channels_game(pool, season, game_id, text_channel.id, voice_channel_1.id, voice_channel_2.id)
    await set_clans_game(pool, season, game_id, clan_name_1, clan_name_2)
    await set_clan_members_game(pool, season, game_id, member_clan_1, member_clan_2)
