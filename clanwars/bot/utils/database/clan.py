import asyncpg
from clanwars.bot.utils.database.objects import Clan


async def fetch_clan(pool: asyncpg.pool.Pool, name: str = None, owner_id: int = None):
    if name is not None:
        clan = await pool.fetchrow("SELECT * FROM clans WHERE clan_name=$1", name)
    elif owner_id is not None:
        clan = await pool.fetchrow("SELECT * FROM clans WHERE owner_id=%1", owner_id)
    else:
        return AttributeError("No clan name or owner_id provided")
    if clan is None:
        return None
    return Clan(clan)


async def new_clan(pool: asyncpg.pool.Pool, clan: Clan):
    await pool.execute("INSERT INTO clans (clan_name, owner_id, elo, proof)")
    return