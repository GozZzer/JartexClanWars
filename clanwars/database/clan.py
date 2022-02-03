import asyncpg

from clanwars.database.utils.clan_utils import check_clan_owner, check_clan_member, check_clan_exists, \
    new_clan, get_clan_name, add_member, remove_member, get_tag_by_name, check_clan_tag
from clanwars.database.utils.member_utils import check_member


async def new_register_clan(
        pool: asyncpg.pool.Pool,
        clan_name: str,
        owner_id: int) -> tuple[str, str | None]:
    """
    This function checks if a clan already exists if not it creates it in the database

    :param pool: The database Pool used to save these values
    :param clan_name: The name of the Clan
    :param owner_id: The ID of the Owner of the clan
    :return: tuple[message, clan_name | None]
    """
    check_owner_exists = await check_member(pool, owner_id)
    if check_owner_exists is False:
        return "`%id` is not registered", "None"

    check_name = await check_clan_exists(pool, clan_name)
    if check_name:
        return "The clanname is already used by the owner: `%id`", None

    check_owner = await check_clan_owner(pool, owner_id)
    if check_owner:
        return "The owner owns already **%c_name**", check_owner

    owner_member = await check_clan_member(pool, owner_id)
    if owner_member:
        return "The owner is already a member of **%c_name**", owner_member

    await new_clan(pool, clan_name, owner_id)
    return "The clan **%c_name** is successfully registered", clan_name


async def add_member_to_clan(
        pool: asyncpg.pool.Pool,
        clan_name: str,
        member_id: int) -> tuple[str, str]:
    """
    This function checks if a member is already in a clan if not he adds him to the given clan

    :param pool: The database Pool used to save these values
    :param clan_name: The name of the Clan
    :param member_id: The ID of the member to add to the clan
    :return: tuple[message, clan_name | None]
    """
    checkk_member = await check_member(pool, member_id)
    if checkk_member is False:
        return "`%id` is not registered", "None"

    clan_name_check = await get_clan_name(pool, member_id)
    if clan_name_check:
        return "`%id` is already part of **%c_name**", clan_name_check

    await add_member(pool, member_id, clan_name)
    return "`%id` is now part of **%c_name**", clan_name


async def remove_member_from_clan(
        pool: asyncpg.pool.Pool,
        clan_name: str,
        member_id: int) -> tuple[str, str]:
    """
    This function checks if a member is already in a clan if not he adds him to the given clan

    :param pool: The database Pool used to save these values
    :param clan_name: The name of the Clan
    :param member_id: The ID of the member to remove from the clan
    :return: tuple[message, clan_name | None]
    """
    checkk_member = await check_member(pool, member_id)
    if checkk_member is False:
        return "`%id` is not registered", "None"

    clan_name_check = await get_clan_name(pool, member_id)
    if clan_name_check == clan_name:
        await remove_member(pool, member_id, clan_name=clan_name)
        return "`%id` is now removed from **%c_name**", clan_name
    else:
        return "`%id` is not part of **%c_name**", clan_name


async def change_tag_clan(
        pool: asyncpg.pool.Pool,
        clan_name: str,
        new_tag: str) -> tuple[str, str, str]:
    old_tag = await get_tag_by_name(pool, clan_name)
    if old_tag == new_tag:
        return "The Tag is already set to **%tag**", new_tag, clan_name

    check_tag = await check_clan_tag(pool, new_tag)
    if check_tag:
        return "The Tag: **%tag** is already used by **%c_name**", new_tag, check_tag

    await pool.execute("UPDATE clan SET tag=$1 WHERE name=$2", new_tag, clan_name)
    return "The Tag is now set to: **%tag**", new_tag, clan_name
