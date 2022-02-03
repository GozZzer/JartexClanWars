from asyncpg.pool import Pool

from clanwars.database.utils.member_utils import check_member, check_ign, check_aliases, new_member, change_ign, get_aliases, add_alias, remove_alias


async def register_new_member(
        pool: Pool,
        member_id: int = None,
        ign: str = None) -> tuple[str, int, str]:
    """
    This function checks if a member is already registered if not it registers it with the given values

    :param pool: The database Pool used to save these values
    :param member_id: The ID of the member
    :param ign: The InGameName of the member
    :return: tuple[message, member_id, ign | None] | tuple[message, member_id]
    """

    check_member_id = await check_member(pool, member_id)
    if check_member_id:
        if check_member_id == ign:
            return "%id is already registered", member_id, ign
        return "%id is already registered as **%name**", member_id, check_member_id

    checkk_ign = await check_ign(pool, ign)
    if checkk_ign:
        return "**%name** is already registered for %id", checkk_ign, ign

    checkk_aliases = await check_aliases(pool, ign)
    if check_aliases:
        return "**%name** is already a alias for %id", checkk_aliases, ign

    await new_member(pool, member_id, ign)
    return "%id is now registered as **%name**", member_id, ign


async def change_ign_member(
        pool: Pool,
        member_id: int = None,
        new_ign: str = None) -> tuple[str, int, str]:
    """
    Change the ign of a member

    :param pool: The database pool to save the data
    :param member_id: The ID of the member
    :param new_ign: The new ign
    :return: tuple[message, member_id, ign]
    """
    check_member_id = await check_member(pool, member_id)
    if not check_member_id:
        return "%id is not registered", member_id, new_ign

    if check_member_id == new_ign:
        return "%id's IGN is already set to **%ign**", member_id, new_ign

    checkk_ign = await check_ign(pool, new_ign)
    if checkk_ign:
        return "**%ign** is already the ign of %id", checkk_ign, new_ign

    checkk_aliases = await check_aliases(pool, new_ign)
    if checkk_aliases:
        return "**%ign** is already an alias of %id", checkk_aliases, new_ign

    await change_ign(pool, member_id, new_ign)
    return "%id's ign is now set to **%ign**", member_id, new_ign


async def add_alias_member(
        pool: Pool,
        member_id: int = None,
        alias: str = None) -> tuple[str, int, str]:
    """
    Add an alias to an account

    :param pool: The database pool to save the data
    :param member_id: The ID of the member
    :param alias: The alias to add
    :return: tuple[message, member_id, alias]
    """
    check_member_id = await check_member(pool, member_id)
    if not check_member_id:
        return "%id is not registered", member_id, alias

    if check_member_id == alias:
        return "%id's IGN is set to **%alias**", member_id, alias

    aliases = await get_aliases(pool, member_id)
    if alias in aliases:
        return "**%alias** is already a alias of %id", member_id, alias

    checkk_ign = await check_ign(pool, alias)
    if checkk_ign:
        return "**%alias** is the ign of %id", checkk_ign, alias

    checkk_aliases = await check_aliases(pool, alias)
    if checkk_aliases:
        return "**%alias** is already an alias of %id", checkk_aliases, alias

    await add_alias(pool, member_id, alias)
    return "**%alias** is now an alias of %id", member_id, alias


async def remove_alias_member(
        pool: Pool,
        member_id: int = None,
        alias: str = None) -> tuple[str, int, str]:
    """
    Remove an alias from an account

    :param pool: The database pool to save the data
    :param member_id: The ID of the member
    :param alias: The alias to remove
    :return: tuple[message, member_id, alias]
    """
    check_member_id = await check_member(pool, member_id)
    if not check_member_id:
        return "%id is not registered", member_id, alias

    if check_member_id == alias:
        return "You can't change %id's ign like this", member_id, alias

    aliases = await get_aliases(pool, member_id)
    if alias not in aliases:
        return "**%alias** is not in %id aliases", member_id, alias

    await remove_alias(pool, member_id, alias)
    return "**%alias** is now removed from %id aliases", member_id, alias
