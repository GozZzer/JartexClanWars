#  MIT License
#
#  Copyright (c) 2022 GozZzer
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
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import asyncio
import logging
import socket

import asyncpg

from clanwars.utils import get_config


def extract_values(data: dict):
    values = {}
    conditions = {}
    for key in data:
        if key.startswith("v_"):
            values[key[2:]] = data[key]
        else:
            conditions[key] = data[key]
    return values, conditions


def query_update_value(table, column, value, **conditions):
    exe = f"UPDATE {table} SET {column}=\'{value}\' WHERE"
    for key in conditions:
        exe += f" {key}=\'{conditions[key]}\' AND"
    return exe[:-4]


def query_update_values(table, **kwargs):
    values, conditions = extract_values(kwargs)
    exe = f"UPDATE {table} SET"
    for key in values:
        exe += f" {key}=\'{values[key]}\',"
    exe = exe[:-1] + " WHERE"
    for key in conditions:
        exe += f" {key}=\'{conditions[key]}\' AND"
    return exe[:-4]


def query_insert_into(table, **values):
    exe = f"INSERT INTO {table}("
    exe2 = f" VALUES ("
    for key in values:
        exe += f"{key}, "
        if isinstance(values[key], str):
            exe2 += f"\'{values[key]}\', "
        else:
            exe2 += f"{values[key]}, "
    exe = exe[:-2] + ")"
    exe += exe2[:-2] + ")"
    return exe


def query_select(table, *select, **conditions):
    if select[0] == "*":
        exe = f"SELECT * FROM {table} WHERE"
    else:
        exe = f"SELECT ({', '.join(select)}) FROM {table} WHERE"
    for key in conditions:
        exe += f" {key}=\'{conditions[key]}\' AND"
    return exe[:-4]


def query_create_table(table, pk, **columns):
    exe = f"CREATE TABLE {table} ("
    for col in columns:
        exe += f"{col} {columns[col]},"
    exe += f" PRIMARY KEY ({pk}))"
    return exe


class Database:
    def __init__(self):
        self.pool: asyncpg.pool.Pool | None = None
        self.database_config = get_config()["database"]
        self.logger = logging.getLogger("asyncpg.database")

    async def create_database_pool(self):
        available_hosts = self.database_config["host"]
        pool = None
        if isinstance(available_hosts, str):
            available_hosts = [available_hosts]
        for host in available_hosts:
            try:
                pool = await asyncpg.create_pool(
                    host=host,
                    user=self.database_config["user"],
                    password=self.database_config["password"],
                    database=self.database_config["name"],
                    timeout=20
                )
                self.database_config["host"] = host
                break
            except asyncpg.exceptions.InvalidPasswordError:
                self.logger.error("Check the password and the username if they are valid")
            except asyncpg.exceptions.InvalidCatalogNameError:
                self.logger.error(f"I am not able to connect to the database: {self.database_config['name']}")
            except socket.gaierror:
                self.logger.error(f"I am not able to get address info of {host}")
            except asyncio.exceptions.CancelledError:
                self.logger.error(f"Cancelled the connecting to {host}")

        if pool is None:
            self.logger.info("I am running without a database")
        else:
            self.logger.info(f"I am successfully connected to the database running on {self.database_config['host']}")
            self.pool = pool

    async def _execute(self, exe, *args):
        async with self.pool.acquire() as connection:
            await connection.execute(exe, *args)

    async def _fetch(self, exe, *args):
        async with self.pool.acquire() as connection:
            return await connection.fetch(exe, *args)
        # asyncpg.exceptions.UndefinedColumnError
        # asyncpg.exceptions.UndefinedTableError

    async def update_value(self, table, column, value, **conditions):
        await self._execute(query_update_value(table, column, value, **conditions))

    async def update_values(self, table, **kwargs):
        await self._execute(query_update_values(table, **kwargs))

    async def insert_into(self, table, **values):
        await self._execute(query_insert_into(table, **values))

    async def select(self, table, *select, **conditions):
        return await self._fetch(query_select(table, *select, **conditions))

    async def create_table(self, table, pk, **columns):
        await self._execute(query_create_table(table, pk, **columns))
