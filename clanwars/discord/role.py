import hikari
import tanjun


async def create_clan_role(
        ctx: tanjun.abc.Context,
        clan_name: str) -> hikari.Role:
    """
    Creates a role with the given clan_name

    :param ctx: Context of the current command
    :param clan_name: The name of the clan to create the role
    :return: The created role
    """
    return await ctx.rest.create_role(ctx.get_guild(), name=clan_name)


async def delete_clan_role(
        ctx: tanjun.abc.Context,
        clan_name: str) -> bool:
    """
    Deletes the role with the given clan_name

    :param ctx: Context of the current command
    :param clan_name: The name of the clan to delete the role
    :return: if the role got deleted
    """
    try:
        role = [role for role in ctx.get_guild().get_roles() if ctx.get_guild().get_role(role).name == clan_name][0]
    except IndexError:
        return None
    try:
        await ctx.rest.delete_role(ctx.get_guild(), role)
        return True
    except hikari.NotFoundError:
        return False


async def add_clan_role(
        ctx: tanjun.abc.Context,
        clan_name: str,
        member_id: int) -> hikari.Role | None:
    """
    This role adds the role with the name of the clan to the member

    :param ctx: Context of the current command
    :param clan_name: The name of the clan
    :param member_id: The ID of the member to add the role to
    :return: The added role
    """
    guild = ctx.get_guild()
    member = guild.get_member(member_id)
    try:
        role = [role for role in ctx.get_guild().get_roles() if ctx.get_guild().get_role(role).name == clan_name][0]
    except IndexError:
        return None
    await member.add_role(role, reason=f"{member} is part of {clan_name}")
    return role


async def remove_clan_role(
        ctx: tanjun.abc.Context,
        clan_name: str,
        member_id: int) -> hikari.Role | None:
    """
    This role removes the role with the name of the clan to the member

    :param ctx: Context of the current command
    :param clan_name: The name of the clan
    :param member_id: The ID of the member to remove the role from
    :return: The removed role
    """
    guild = ctx.get_guild()
    member = guild.get_member(member_id)
    try:
        role = [role for role in ctx.get_guild().get_roles() if ctx.get_guild().get_role(role).name == clan_name][0]
    except IndexError:
        return None
    await member.remove_role(role, reason=f"{member} is not part of {clan_name} anymore")
    return role
