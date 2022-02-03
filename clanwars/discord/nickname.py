import asyncpg
import hikari
import tanjun

from clanwars.database.utils.clan_utils import get_tag_by_name
from clanwars.database.utils.member_utils import check_member


async def update_nick(
        ctx: tanjun.abc.Context,
        pool: asyncpg.pool.Pool,
        member_id: int,
        clan_name: str = None) -> bool:
    ign = await check_member(pool, member_id)
    guild = ctx.get_guild()
    member = guild.get_member(member_id)
    if clan_name is None:
        try:
            await member.edit(nick=f"{ign}")
            return True
        except hikari.ForbiddenError:
            return False
    else:
        tag = await get_tag_by_name(pool, clan_name)
    try:
        if tag:
            await member.edit(nick=f"[{tag}] {ign}")
        else:
            await member.edit(nick=f"[{clan_name}] {ign}")
        return True
    except hikari.ForbiddenError:
        return False

