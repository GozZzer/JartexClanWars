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
from datetime import datetime


###################
# Get Information #
###################
async def get_current_season(
        pool: asyncpg.pool.Pool) -> int | str:
    """
    Returns the current season

    :param pool: The Database Pool to get the data
    :return: The current season
    """
    current_season = await pool.fetchval("SELECT max(season+1) FROM seasons")
    current_season -= 1
    if current_season == 0:
        return 'beta'
    return current_season


async def get_start_season(
        pool: asyncpg.pool.Pool,
        season: int) -> datetime | None:
    """
    Returns the start of the given season

    :param pool: The Database Pool to get the data
    :param season: The season to get the starting date of
    :return: The start of the season
    """
    start = await pool.fetchrow("SELECT started FROM seasons WHERE season=$1", season+1)
    return start["started"] if start else None


async def get_end_season(
        pool: asyncpg.pool.Pool,
        season: int) -> datetime | None:
    """
    Returns the end of the given season

    :param pool: The Database Pool to get the data
    :param season: The season to get the ending date of
    :return: The end of the season
    """
    end = await pool.fetchrow("SELECT ended FROM seasons WHERE season=$1", season+1)
    return end["ended"] if end else None


async def get_games_season(
        pool: asyncpg.pool.Pool,
        season: int) -> int | None:
    """
    Returns the games of the given season

    :param pool: The Database Pool to get the data
    :param season: The season to get the games 
    :return: The games of the season
    """
    games = await pool.fetchrow("SELECT games FROM seasons WHERE season=$1", season+1)
    return games["games"] if games else None


async def get_registers_season(
        pool: asyncpg.pool.Pool,
        season: int) -> int | None:
    """
    Returns the registers of the given season

    :param pool: The Database Pool to get the data
    :param season: The season to get the registers 
    :return: The registers of the season
    """
    reg = await pool.fetchrow("SELECT new_registers FROM seasons WHERE season=$1", season+1)
    return reg["new_registers"] if reg else None


async def get_full_season(
        pool: asyncpg.pool.Pool,
        season: int) -> dict | None:
    """
    Get the whole data of a season

    :param pool: The Database Pool to get the data
    :param season: The season
    :return: The data of the whole season
    """
    data = await pool.fetchrow("SELECT * FROM seasons WHERE season=$1", season+1)
    return data if data else None


######################
# Update/Create Clan #
######################
async def new_season(
    pool: asyncpg.pool.Pool) -> int | None:
    """
    Start a new season

    :param pool: The database Pool to save the data
    :return: The created season
    """
    insert = await pool.fetchval("INSERT INTO seasons DEFAULT VALUES RETURNING season")
    return insert["season"] if insert else None


async def end_season(
        pool: asyncpg.pool.Pool,
        season: int) -> bool:
    """
    End the gives season

    :param pool: The Database Pool to save the data
    :param season: The season to end
    :return: If it got executed
    """
    check = await pool.execute("UPDATE seasons SET ended=$1 WHERE season=$2", datetime.utcnow(), season+1)
    return True if check.endswith("1") else False


async def edit_games(
        pool: asyncpg.pool.Pool,
        season: int,
        games: int) -> bool:
    """
    Update the games of the gives season

    :param pool: The Database Pool to save the data
    :param season: The season to update the game
    :param games: The amount of games
    :return: If it got executed
    """
    check = await pool.execute("UPDATE seasons SET games=$1 WHERE season=$2", games, season + 1)
    return True if check.endswith("1") else False


async def edit_registers(
        pool: asyncpg.pool.Pool,
        season: int,
        registers: int) -> bool:
    """
    Update the registers of the gives season

    :param pool: The Database Pool to save the data
    :param season: The season to update the game
    :param registers: The amount of registers
    :return: If it got executed
    """
    check = await pool.execute("UPDATE seasons SET new_registers=$1 WHERE season=$2", registers, season + 1)
    return True if check.endswith("1") else False
