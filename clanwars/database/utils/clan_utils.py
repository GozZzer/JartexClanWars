import random
import asyncpg


###################
# Get Information #
###################
async def check_clan_exists(
        pool: asyncpg.pool.Pool,
        clan_name: str) -> int | None:
    """
    This function checks if a clan_name already exists

    :param pool: The database Pool used to check these values
    :param clan_name: The name of the clan you want to check
    :return: owner_id | None
    """
    check_name = await pool.fetchrow("SELECT owner_id FROM clan WHERE name=$1 AND deleted=False", clan_name)
    return check_name["owner_id"] if check_name else None


async def check_clan_owner(
        pool: asyncpg.pool.Pool,
        owner_id: int) -> str | None:
    """
    This function checks if the member already owns a clan

    :param pool: The database Pool used to check these values
    :param owner_id: The ID of teh member to check if he already owns a clan
    :return: clan_name | None
    """
    check = await pool.fetchrow("SELECT name FROM clan WHERE owner_id=$1 AND deleted=False", owner_id)
    return check["name"] if check else None


async def check_clan_member(
        pool: asyncpg.pool.Pool,
        member_id: int) -> str | None:
    """
    This function checks if the member is already a part of a clan

    :param pool: The database Pool used to check these values
    :param member_id: The ID of the member to check
    :return: clan_name | None
    """
    check = await pool.fetchrow("SELECT name FROM clan WHERE $1 = ANY(members) AND deleted=False", member_id)
    return check["name"] if check else None


async def check_clan_tag(
        pool: asyncpg.pool.Pool,
        tag: str) -> str | None:
    """
    This function checks if the Tag is already in use

    :param pool: The database Pool used to check these values
    :param tag: The tag to check
    :return: clan_name | None
    """
    clan_name = await pool.fetchrow("SELECT name FROM clan WHERE tag=$1 AND deleted=False", tag)
    return clan_name["name"] if clan_name else None


async def get_tag_by_name(
        pool: asyncpg.pool.Pool,
        clan_name: str) -> str | None:
    check_tag = await pool.fetchrow("SELECT tag FROM clan WHERE name=$1 AND deleted=False", clan_name)
    return check_tag["tag"] if check_tag else None


async def get_clan_name(
        pool: asyncpg.pool.Pool,
        member_id: int) -> str | None:
    """
    This function returns the clan the member is part of

    :param pool: The database Pool used to check these values
    :param member_id: The ID of the member to check the clan_name
    :return: clan_name | None
    """
    clan_owns = await check_clan_owner(pool, member_id)
    if clan_owns:
        return clan_owns

    clan_member = await check_clan_member(pool, member_id)
    if clan_member:
        return clan_member

    return None


async def get_clan_tag(
        pool: asyncpg.pool.Pool,
        member_id: int) -> str | None:
    """
    This function returns the tag the member is part of

    :param pool: The database Pool used to check these values
    :param member_id: The ID of the member to check the clan_name
    :return: clan_name | None
    """
    clan_name = await check_clan_owner(pool, member_id)
    if not clan_name:
        clan_name = await check_clan_member(pool, member_id)
    return await get_tag_by_name(pool, clan_name) if clan_name else None


async def get_clan_role(
        pool: asyncpg.pool.Pool,
        clan_name: str) -> int | None:
    """
    This function returns the role_id of the clan role.

    :param pool:
    :param clan_name:
    :return: role_id | None
    """
    role_id = await pool.fetchrow("SELECT role_id FROM clan WHERE name=$1", clan_name)
    return role_id["role_id"] if role_id else None


async def get_clan_member(
        pool: asyncpg.pool.Pool,
        clan_name: str) -> list[int | None]:
    """
    This function returns a list of all member ids of a clan

    :param pool: The Database Pool to get the data of
    :param clan_name: The name of the clan
    :return: list[member_id, None]
    """
    member = await pool.fetchrow("SELECT members FROM clan WHERE name=$1 AND deleted=False", clan_name)
    return member["members"] if member else None


######################
# Update/Create Clan #
######################
async def new_clan(
        pool: asyncpg.pool.Pool,
        clan_name: str,
        owner_id: int) -> bool:
    """
    This function adds a new clan to the database

    :param pool: The database Pool used to save the data
    :param clan_name: The name of the clan you want to create
    :param owner_id: The ID of the owner the clan belongs to
    :return: bool True if it got executed else False
    """
    exe = await pool.execute("INSERT INTO clan (name, owner_id) VALUES ($1, $2)", clan_name, owner_id)
    if exe.endswith("1"):
        return True
    return False


async def add_member(
        pool: asyncpg.pool.Pool,
        member_id: int,
        clan_name: str = None,
        owner_id: int = None) -> bool:
    """
    Adds the member to the clan

    :param pool: The database Pool used to save the data
    :param clan_name: The name of the clan to add this member to
    :param member_id: The ID of the member to add to the clan
    :param owner_id: The ID of the owner of the clan to add this member to
    :return: bool True if it got executed else False
    """
    if clan_name is None and owner_id is None:
        return False

    if clan_name:
        exe = await pool.execute("UPDATE clan SET members=array_append(members, $1) WHERE name=$2", member_id, clan_name)
        if exe.endswith("1"):
            return True

    if owner_id:
        exe = await pool.execute("UPDATE clan SET members=array_append(members, $1) WHERE owner_id=$2", member_id, owner_id)
        if exe.endswith("1"):
            return True

    return False


async def remove_member(
        pool: asyncpg.pool.Pool,
        member_id: int,
        is_in_was: bool = None,
        clan_name: str = None,
        owner_id: str = None) -> bool:
    """
    Removes the member from the clan and adds it to the was_member

    :param pool: The database Pool used to save the data
    :param member_id: The ID of the member to remove to the clan
    :param is_in_was: If the member is already part of the was_member
    :param clan_name: The name of the clan to remove this member to
    :param owner_id: The ID of the owner of the clan to remove this member to
    :return: bool True if it got executed else False
    """
    if clan_name is None and owner_id is None:
        return False

    if is_in_was is None:
        was_mem = await pool.fetchrow("SELECT clan FROM clan WHERE $1=any(was_member) AND name=$2", member_id, clan_name)
        if was_mem:
            is_in_was = True
        else:
            is_in_was = False

    if clan_name:
        if is_in_was is False:
            exe = await pool.execute("UPDATE clan SET members=array_remove(members, $1), was_member=array_append(was_member, $1) WHERE name=$2;", member_id, clan_name)
        else:
            exe = await pool.execute("UPDATE clan SET members=array_remove(members, $1) WHERE name=$2;", member_id, clan_name)
        if exe.endswith("1"):
            return True

    if owner_id:
        if is_in_was is False:
            exe = await pool.execute("UPDATE clan SET members=array_remove(members, $1), was_member=array_append(was_member, $1) WHERE owner_id=$2", member_id, owner_id)
        else:
            exe = await pool.execute("UPDATE clan SET members=array_remove(members, $1) WHERE owner_id=$2", member_id, owner_id)
        if exe.endswith("1"):
            return True

    return False


async def delete_clan(
        pool: asyncpg.pool.Pool,
        clan_name: str = None,
        owner_id: int = None) -> bool:
    """
    "Deletes" a clan

    :param pool: The database Pool used to save the data
    :param clan_name: The name of the clan to delete
    :param owner_id: The ID of the owner to delete
    :return: bool True if it got executed else False
    """
    if clan_name is None and owner_id is None:
        return False

    if clan_name:
        exe = await pool.execute("UPDATE clan SET name=$1, deleted=True WHERE name=$2", f"d{random.randint(1000000, 999999999)}_{clan_name}", clan_name)
        if exe.endswith("1"):
            return True

    if owner_id:
        clan_name = await get_clan_name(pool, owner_id)
        exe = await pool.execute("UPDATE clan SET name=$1, deleted=True WHERE owner_id=$2", f"d{random.randint(1000000, 999999999)}_{clan_name}", owner_id)
        if exe.endswith("1"):
            return True

    return False


async def enable_clan(
        pool: asyncpg.pool.Pool,
        clan_name: str = None,
        owner_id: int = None) -> bool:
    """
    Enables a clan

    :param pool: The database Pool used to save the data
    :param clan_name: The name of the clan to enable
    :param owner_id: The ID of the owner to enable
    :return: bool True if it got executed else False
    """
    if clan_name is None and owner_id is None:
        return False

    if clan_name:
        exe = await pool.execute("UPDATE clan SET enabled=True WHERE name=$1", clan_name)
        if exe.endswith("1"):
            return True

    if owner_id:
        exe = await pool.execute("UPDATE clan SET enabled=True WHERE owner_id=$1", owner_id)
        if exe.endswith("1"):
            return True

    return False


async def disable_clan(
        pool: asyncpg.pool.Pool,
        clan_name: str = None,
        owner_id: int = None) -> bool:
    """
    Disables a clan

    :param pool: The database Pool used to save the data
    :param clan_name: The name of the clan to disable
    :param owner_id: The ID of the owner to disable
    :return: bool True if it got executed else False
    """
    if clan_name is None and owner_id is None:
        return False

    if clan_name:
        exe = await pool.execute("UPDATE clan SET enabled=False WHERE name=$1", clan_name)
        if exe.endswith("1"):
            return True

    if owner_id:
        exe = await pool.execute("UPDATE clan SET enabled=False WHERE owner_id=$1", owner_id)
        if exe.endswith("1"):
            return True

    return False


async def change_tag(
        pool: asyncpg.pool.Pool,
        new_tag: str,
        clan_name: str = None,
        owner_id: int = None) -> bool:
    """
    Disables a clan

    :param pool: The database Pool used to save the data
    :param new_tag: The new tag of the clan
    :param clan_name: The name of the clan to disable
    :param owner_id: The ID of the owner to disable
    :return: bool True if it got executed else False
    """
    if clan_name is None and owner_id is None:
        return False

    if clan_name:
        exe = await pool.execute("UPDATE clan SET tag=$2 WHERE name=$1", clan_name, new_tag)
        if exe.endswith("1"):
            return True

    if owner_id:
        exe = await pool.execute("UPDATE clan SET tag=$2 WHERE owner_id=$1", owner_id, new_tag)
        if exe.endswith("1"):
            return True

    return False


async def approve_clan(
        pool: asyncpg.pool.Pool,
        clan_name: str = None,
        owner_id: int = None) -> bool:
    """
    Approve a clan

    :param pool: The database Pool used to save the data
    :param clan_name: The name of the clan to approve
    :param owner_id: The ID of the owner to approve
    :return: bool True if it got executed else False
    """
    if clan_name is None and owner_id is None:
        return False

    if clan_name:
        exe = await pool.execute("UPDATE clan SET approved=True WHERE name=$1", clan_name)
        if exe.endswith("1"):
            return True

    if owner_id:
        exe = await pool.execute("UPDATE clan SET approved=True WHERE owner_id=$1", owner_id)
        if exe.endswith("1"):
            return True

    return False


async def undo_approve_clan(
        pool: asyncpg.pool.Pool,
        clan_name: str = None,
        owner_id: int = None) -> bool:
    """
    Undo the approval of a clan

    :param pool: The database Pool used to save the data
    :param clan_name: The name of the clan to undo the approval
    :param owner_id: The ID of the owner to undo the approval
    :return: bool True if it got executed else False
    """
    if clan_name is None and owner_id is None:
        return False

    if clan_name:
        exe = await pool.execute("UPDATE clan SET approved=False WHERE name=$1", clan_name)
        if exe.endswith("1"):
            return True

    if owner_id:
        exe = await pool.execute("UPDATE clan SET approved=False WHERE owner_id=$1", owner_id)
        if exe.endswith("1"):
            return True

    return False


async def set_role_id(
        pool: asyncpg.pool.Pool,
        role_id: int,
        clan_name: str = None,
        owner_id: int = None) -> bool:
    """
    This function sets the role id of the given clan role

    :param pool: The database Pool used to save the data
    :param clan_name: The name of the clan to set the
    :param owner_id: The ID of the owner of the clan
    :param role_id: The ID of the role
    :return:
    """
    if clan_name is None and owner_id is None:
        return False

    if clan_name:
        exe = await pool.execute("UPDATE clan SET role_id=$1 WHERE name=$2 AND deleted=False", role_id, clan_name)
        if exe.endswith("1"):
            return True

    if owner_id:
        exe = await pool.execute("UPDATE clan SET role_id=$1 WHERE owner_id=$2 AND deleted=False", role_id, owner_id)
        if exe.endswith("1"):
            return True
    
