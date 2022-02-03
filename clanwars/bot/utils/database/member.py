from typing import Optional
from asyncpg.pool import Pool

from clanwars.bot.utils.database.objects import Member


async def fetch_member(user_id: int = None, pool: Pool = None) -> Optional[Member]:
    member_db = await pool.fetchrow("SELECT * FROM members WHERE user_id = $1", user_id)
    if member_db is None:
        return None
    else:
        return Member(**member_db)


async def update_member(user_id: int = None, pool: Pool = None, update=None, value=None) -> bool:
    if update is None:
        return False
    if not isinstance(update, str):
        if len(update) == 1:
            update = update[0]
        else:
            update_exe = ""
            for i in range(0, len(update)):
                update_exe += f"{update[i]}=${i + 1}, "
            update = update_exe[:-2]

    exe = f"UPDATE members SET {update}=$1 WHERE user_id = $2"
    execute = await pool.execute(exe, value, user_id)
    if execute[-1] == 0:
        return False
    else:
        return True


async def new_member(member: Member, pool: Pool = None) -> bool:
    execute = await pool.execute("INSERT INTO members (user_id, ign, other_igns, clan) VALUES ($1, $2, $3, $4)", *list(member))
