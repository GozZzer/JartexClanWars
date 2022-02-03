import asyncpg
import json


def get_config():
    with open("clanwars/bot/config.json", "r") as config_file:
        return json.load(config_file)


async def setup_postgres_database_pool(database: str = "clanwars"):
    CONFIG = get_config()
    pool: asyncpg.pool.Pool = await asyncpg.create_pool(
        host=CONFIG["database"]["host"],  # where db is hosted
        database=database,  # name of database
        user=CONFIG["database"]["user"],  # database username
        password=CONFIG["database"]["password"],  # password which goes with user_id
    )
    return pool



