import asyncpg
import datetime

from clanwars.bot.utils.setup import setup_postgres_database_pool


async def start_new_season(pool: asyncpg.pool.Pool):
    data = await pool.fetchrow("SELECT MAX(season) FROM seasons")
    current_season = data["max"]
    if current_season is None:
        current_season = 0
    await pool.execute("INSERT INTO seasons (start_date) VALUES ($1)", datetime.datetime.utcnow())
    await pool.execute(f"CREATE DATABASE season_{current_season + 1}")
    season_pool = await setup_postgres_database_pool(f"season_{current_season + 1}")
    await season_pool.execute(open("/clanwars/bot/utils/database/sqls/new_season.sql", "r").read())

    await season_pool.close()
    return "Done"
