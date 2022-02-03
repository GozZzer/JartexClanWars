import asyncpg


###################
# Get Information #
###################
async def check_member(
        pool: asyncpg.pool.Pool,
        member_id: int) -> str | None:
    """
    This functions returns the ingamename of the member

    :param pool: The Database Pool to get the data of
    :param member_id: The ID of the Member to get the ign of
    :return: ign | None
    """
    ign = await pool.fetchrow("SELECT ign FROM member WHERE member_id=$1", member_id)
    return ign["ign"] if ign else None


async def check_ign(
        pool: asyncpg.pool.Pool,
        ign: str) -> int | None:
    """
    Check if the ign is already used by someone

    :param pool: The Database Pool to get the data from
    :param ign: The ign to check if it exists
    :return: member_id | None
    """
    id = await pool.fetchrow("SELECT member_id FROM member WHERE ign=$1", ign)
    return id["member_id"] if id else None


async def check_aliases(
        pool: asyncpg.pool.Pool,
        ign: str) -> int | None:
    """
    Check if an ign is already used as an alias

    :param pool: The Database Pool to get the data
    :param ign: The ign of the member
    :return: member_id | None
    """
    alias = await pool.fetchrow("SELECT member_id FROM member WHERE $1 = any(aliases)", ign)
    return alias["member_id"] if alias else None


async def check_banned(
        pool: asyncpg.pool.Pool,
        member_id: int) -> bool | None:
    """
    This function checks if a member is banned

    :param pool: The Database Pool to get the data
    :param member_id: The ID of the member
    :return: If the member is banned or not
    """

    ban = await pool.fetchrow("SELECT banned FROM member WHERE member_id=$1", member_id)
    return ban["banned"] if ban else None


async def check_warns(
        pool: asyncpg.pool.Pool,
        member_id: int) -> int | None:
    """
    This function gets the amount of the warns of a user

    :param pool: The Database Pool to get the data
    :param member_id: The ID of the member
    :return: amount of warns | None
    """
    warns = await pool.fetchrow("SELECT warns FROM member WHERE member_id=$1", member_id)
    return warns["warns"] if warns else None


async def get_aliases(
        pool: asyncpg.pool.Pool,
        member_id: int) -> list[str]:
    """
    Returns the list of the aliases of a member

    :param pool: The Database Pool to get the data
    :param member_id: The ID of the member
    :return: the list of teh aliases
    """
    aliases = await pool.fetchrow("SELECT aliases FROM member WHERE member_id=$1", member_id)
    return aliases["aliases"] if aliases else None


########################
# Update/Create Member #
########################
async def new_member(
        pool: asyncpg.pool.Pool,
        member_id: int,
        ign: str) -> bool:
    """
    Insert a new member to member table

    :param pool: The database pool to save the data
    :param member_id: The ID of the member
    :param ign: The Ign of the member
    :return: If it got executed
    """
    exe = await pool.execute("INSERT INTO member (member_id, ign) VALUES ($1, $2)", member_id, ign)
    if exe.endswith("1"):
        return True
    return False


async def change_ign(
        pool: asyncpg.pool.Pool,
        member_id: int,
        new_ign: str) -> bool:
    """
    This function changes the ign of a member

    :param pool: The database Pool to save the data
    :param member_id: The ID of the member
    :param new_ign: The new ign of the member
    :return:
    """
    exe = await pool.execute("UPDATE member SET ign=$1 WHERE member_id=$2", new_ign, member_id)
    if exe.endswith("1"):
        return True
    return False


async def add_alias(
        pool: asyncpg.pool.Pool,
        member_id: int,
        alias: str) -> bool:
    """
    This function adds a new alias

    :param pool: The database Pool to save the data
    :param member_id: The ID of the member
    :param alias: The alias to add
    :return: If it got executed
    """
    exe = await pool.execute("UPDATE member SET aliases=array_append(aliases, $1) WHERE member_id=$2", alias, member_id)
    if exe.endswith("1"):
        return True
    return False


async def remove_alias(
        pool: asyncpg.pool.Pool,
        member_id: int,
        alias: str) -> bool:
    """
    Removes an alias

    :param pool: The database Pool to save the data
    :param member_id: The ID of the member
    :param alias: The alias to remove
    :return: If it got execute
    """

    exe = await pool.execute("UPDATE member SET aliases=array_remove(aliases, $1) WHERE member_id=$2", alias, member_id)
    if exe.endswith("1"):
        return True
    return False


async def add_warn(
        pool: asyncpg.pool.Pool,
        member_id: int,
        warns: int = 1) -> bool:
    """
    Adds the set amount (default 1) to the warns

    :param pool: The database Pool to save the data
    :param member_id: The ID of the member
    :param warns: The amount of warns
    :return: If it got executed
    """
    exe = await pool.execute("UPDATE member SET warns=warns+$2 WHERE member_id=$1", member_id, warns)
    if exe.endswith("1"):
        return True
    return False


async def remove_warn(
        pool: asyncpg.pool.Pool,
        member_id: int,
        warns: int = 1) -> bool:
    """
    Removes the given amount of warns from a member

    :param pool: The database to save the data
    :param member_id: The ID of the member
    :param warns: The amount of warns
    :return: If it got executed
    """

    exe = await pool.execute("UPDATE member SET warns=warns-$2 WHERE member_id=$1", member_id, warns)
    if exe.endswith("1"):
        return True
    return False


async def ban_member(
        pool: asyncpg.pool.Pool,
        member_id: int) -> bool:
    """
    Banns the member

    :param pool: The database pool to save the data
    :param member_id: Teh ID of the member
    :return: If it got executed
    """
    exe = await pool.execute("UPDATE member SET banned=TRUE WHERE member_id=$1", member_id)
    if exe.endswith("1"):
        return True
    return False


async def unban_member(
        pool: asyncpg.pool.Pool,
        member_id: int) -> bool:
    """
    Unbans a member

    :param pool: The database pool to save the data
    :param member_id: The ID of the member
    :return: If it got executed
    """
    exe = await pool.execute("UPDATE member SET banned=FALSE WHERE member_id=$1", member_id)
    if exe.endswith("1"):
        return True
    return False
