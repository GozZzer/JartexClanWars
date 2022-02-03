import tanjun

from clanwars.database.utils.clan_utils import check_clan_owner
from clanwars.database.model import Database


async def is_clan_owner(
        ctx: tanjun.abc.Context,
        database: Database = tanjun.inject(type=Database)):
    if await check_clan_owner(database.pool, ctx.author.id):
        return True
    else:
        raise tanjun.CommandError("You do not own a clan")
