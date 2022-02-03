import asyncpg
import logging

from typing import Optional
from clanwars.utils.stuff import get_config


class Database:
    def __init__(self):
        self.config: dict = get_config()["database"]
        self.pool: Optional[asyncpg.pool.Pool] = None
        self.logger = logging.getLogger("postgresql.database")

    async def create_database_pool(self) -> Optional[asyncpg.pool.Pool]:
        try:
            pool = await asyncpg.create_pool(
                host=self.config["host"],
                port=self.config["port"],
                database=self.config["database"],
                user=self.config["user"],
                password=self.config["password"],
            )
        except:
            self.logger.error(f"I am not able to connect to the database running on {self.config['host']}")
            return
        self.pool = pool
        self.logger.info(f"I am connected to the database running on {self.config['host']}")
