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


###################
# Get Information #
###################
async def get_highest_game(
        pool: asyncpg.pool.Pool,
        season: int):
    if season == 0:
        season = "beta"
    maximum = await pool.fetchval(f"SELECT MAX(game_id) FROM games_{season}")
    return maximum if maximum else None


async def get_category_game(
        pool: asyncpg.pool.Pool,
        season: int,
        game: int):
    if season == 0:
        season = "beta"
    cat = await pool.fetchval(f"SELECT category FROM games_{season} WHERE game_id=$1", game)
    return cat["category"] if cat else None


async def get_channels_game(
        pool: asyncpg.pool.Pool,
        season: int,
        game: int):
    if season == 0:
        season = "beta"
    channels = await pool.fetchrow(f"SELECT text_channel, voice_channel_1, voice_channel_2 FROM games_{season} WHERE game_id=$1", game)
    return list(channels) if channels else None


async def get_clans_game(
        pool: asyncpg.pool.Pool,
        season: int,
        game: int):
    if season == 0:
        season = "beta"
    clans = await pool.fetchrow(f"SELECT clan_1, clan_2 FROM games_{season} WHERE game_id=$1", game)
    return list(channels) if channels else None


async def get_players_game(
        pool: asyncpg.pool.Pool,
        season: int,
        game: int):
    if season == 0:
        season = "beta"
    players = await pool.fetchrow(f"SELECT clan_1_member, clan_2_member FROM games_{season} WHERE game_id=$1", game)
    return list(players) if players else None


#######################
# Update/Create Games #
#######################
async def new_game(
        pool: asyncpg.pool.Pool,
        season: int):
    if season == 0:
        season = "beta"
    game_id = await pool.fetchval(f"INSERT INTO games_{season} SET DEFAULT RETURNING game_id")
    return game_id["game_id"] if game_id else None


async def set_category_game(
        pool: asyncpg.pool.Pool,
        season: int,
        game: int,
        category: int):
    if season == 0:
        season = "beta"
    check = await pool.execute(f"UPDATE games_{season} SET category=$1 WHERE game_id=$2", category, game)
    return True if check.endswith("1") else False


async def set_channels_game(
        pool: asyncpg.pool.Pool,
        season: int,
        game: int,
        text_channel: int,
        voice_channel_1: int,
        voice_channel_2: int):
    if season == 0:
        season = "beta"
    check = await pool.execute(f"UPDATE games_{season} SET text_channel=$1, voice_channel_1=$2, voice_channel_2=$3 WHERE game_id=$4",
                               text_channel, voice_channel_1, voice_channel_2, game)
    return True if check.endswith("1") else False


async def set_clans_game(
        pool: asyncpg.pool.Pool,
        season: int,
        game: int,
        clan_1: int,
        clan_2: int):
    if season == 0:
        season = "beta"
    check = await pool.execute(f"UPDATE games_{season} SET clan_1=$1, clan_2=$2 WHERE game_id=$3", clan_1, clan_2, game)
    return True if check.endswith("1") else False


async def set_clan_members_game(
        pool: asyncpg.pool.Pool,
        season: int,
        game: int,
        members_1: list,
        members_2: list):
    if season == 0:
        season = "beta"
    check = await pool.execute(f"UPDATE games_{season} SET clan_1_member=$1, clan_2_member=$2 WHERE game_id=$3",
                               members_1, members_2, game)
    return True if check.endswith("1") else False
