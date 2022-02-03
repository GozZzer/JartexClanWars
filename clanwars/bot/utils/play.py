from typing import Optional

import asyncpg
import hikari


async def check_clan(
        voice_state: hikari.api.CacheView[hikari.Snowflake, hikari.VoiceState],
        pool: asyncpg.pool.Pool) -> [Optional[str], Optional[int]]:
    clans = {}
    for member in voice_state:
        member_db = await pool.fetchrow("SELECT * FROM members WHERE user_id=$1", member)
        clan = member_db["clan"]
        if clan:
            try:
                clans[clan] += 1
            except KeyError:
                clans[clan] = 1
    if clans == {}:
        return None, None

    clans = dict(sorted(clans.items(), key=lambda item: item[1], reverse=True))
    clan_name = list(clans.keys())[0]
    clan = clans[clan_name]
    return clan_name, clan


