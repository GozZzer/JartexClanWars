import asyncpg

from hikari import Member
from tanjun import CommandError
from tanjun.abc import Context

from clanwars.bot.client import ClanWarsClient


async def can_register(ctx: Context):
    """Checks if a User has the permission admin or the registered"""
    client: ClanWarsClient = ctx.client
    pool: asyncpg.pool.Pool = client.db
    author = ctx.member
    user_db = await pool.fetchrow("SELECT * FROM staff WHERE user_id=$1", author.id)
    if user_db is None:
        raise CommandError("You are not allowed to use this Command")
    else:
        if user_db["active"]:
            if user_db["admin"] is True:
                return True
            elif user_db["register"] is True:
                return True
            else:
                raise CommandError("You are not allowed to use this Command")
        else:
            raise CommandError("You are not allowed to use this Command")


async def can_score(ctx: Context):
    client: ClanWarsClient = ctx.client
    pool: asyncpg.pool.Pool = client.db
    author = ctx.member
    user_db = await pool.fetchrow("SELECT * FROM staff WHERE user_id=$1", author.id)
    if user_db is None:
        raise CommandError("You are not allowed to use this Command")
    else:
        if user_db["active"]:
            if user_db["admin"] is True:
                return True
            elif user_db["score"] is True:
                return True
            else:
                raise CommandError("You are not allowed to use this Command")
        else:
            raise CommandError("You are not allowed to use this Command")


async def can_score_listener(pool: asyncpg.pool.Pool, interactor: Member):
    user_db = await pool.fetchrow("SELECT * FROM staff WHERE user_id=$1", interactor.id)
    if user_db is None:
        return "You are not allowed to use this Command"
    else:
        if user_db["active"]:
            if user_db["admin"] is True:
                return True
            elif user_db["score"] is True:
                return True
            else:
                return"You are not allowed to use this Command"
        else:
            return "You are not allowed to use this Command"


async def can_register_listener(pool: asyncpg.pool.Pool, interactor: Member):
    user_db = await pool.fetchrow("SELECT * FROM staff WHERE user_id=$1", interactor.id)
    if user_db is None:
        return "You are not allowed to use this Command"
    else:
        if user_db["active"]:
            if user_db["admin"] is True:
                return True
            elif user_db["register"] is True:
                return True
            else:
                return "You are not allowed to use this Command"
        else:
            return "You are not allowed to use this Command"


async def is_admin(ctx: Context):
    """Checks if a User has the permission admin"""
    client: ClanWarsClient = ctx.client
    pool: asyncpg.pool.Pool = client.db
    author = ctx.member
    user_db = await pool.fetchrow("SELECT * FROM staff WHERE user_id=$1", author.id)
    if user_db is None:
        raise CommandError("You are not allowed to use this Command")
    else:
        if user_db["active"]:
            if user_db["admin"] is True:
                return True
            else:
                raise CommandError("You are not allowed to use this Command")
        else:
            raise CommandError("You are not allowed to use this Command")


async def is_clan_owner(ctx: Context):
    """Checks if a User owns a Clan"""
    client: ClanWarsClient = ctx.client
    pool: asyncpg.pool.Pool = client.db
    author = ctx.member
    clan_db = await pool.fetchrow("SELECT * FROM clans WHERE owner_id=$1", author.id)
    if clan_db is None:
        raise CommandError("You do not own a Clan")
    else:
        return True


async def was_clan_owner(ctx: Context):
    client: ClanWarsClient = ctx.client
    pool: asyncpg.pool.Pool = client.db
    author = ctx.member
    clan_db = await pool.fetchrow("SELECT * FROM clans WHERE owner_id=$1", author.id)
    if clan_db is None:
        raise CommandError("You didn't owned a clan")
    else:
        if clan_db["deleted"] is True:
            return True
        else:
            raise CommandError("Your clan is not deleted")

