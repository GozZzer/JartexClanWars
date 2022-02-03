import hikari

import tanjun

from clanwars.database import Database, new_register_clan, add_member_to_clan, remove_member_from_clan, change_tag_clan
from clanwars.database.utils.clan_utils import get_clan_name, disable_clan, enable_clan, delete_clan, set_role_id, get_clan_member
from clanwars.discord import create_clan_role, add_clan_role, update_nick, remove_clan_role, delete_clan_role
from clanwars.utils import is_clan_owner




#######################
# Update/Create Clans #
#######################
@tanjun.with_str_slash_option("clan_name", "The name of the clan")
@tanjun.as_slash_command("register_clan", "Register the clan if you own one")
async def register_clan_command(
        ctx: tanjun.abc.SlashContext,
        clan_name: str,
        database: Database = tanjun.inject(type=Database)):
    message, value = await new_register_clan(database.pool, clan_name, ctx.author.id)
    role = await create_clan_role(ctx, clan_name)
    await set_role_id(database.pool, role.id, clan_name)
    await add_clan_role(ctx, clan_name, ctx.author.id)
    await update_nick(ctx, database.pool, ctx.author.id, clan_name)
    await ctx.respond(message.replace("%id", ctx.author.mention).replace("%c_name", value))


@tanjun.with_check(is_clan_owner)
@tanjun.with_member_slash_option("member", "The member you want to add to your clan")
@tanjun.as_slash_command("add_member", "Add a member to your clan")
async def add_member_command(
        ctx: tanjun.abc.SlashContext,
        member: hikari.InteractionMember,
        database: Database = tanjun.inject(type=Database)):
    if ctx.author == member:
        await ctx.respond("You can't add yourself to the clan")
        return
    message, clan_name = await add_member_to_clan(database.pool, await get_clan_name(database.pool, ctx.author.id), member.id)
    await add_clan_role(ctx, await get_clan_name(database.pool, ctx.author.id), member.id)
    await update_nick(ctx, database.pool, member.id, await get_clan_name(database.pool, member.id))
    await ctx.respond(message.replace("%id", str(member)).replace("%c_name", clan_name))


@tanjun.with_check(is_clan_owner)
@tanjun.with_member_slash_option("member", "The member you want to add to your clan")
@tanjun.as_slash_command("remove_member", "Add a member to your clan")
async def remove_member_command(
        ctx: tanjun.abc.SlashContext,
        member: hikari.InteractionMember,
        database: Database = tanjun.inject(type=Database)):
    if ctx.author == member:
        await ctx.respond("You can't remove yourself from the clan")
        return
    await remove_clan_role(ctx, await get_clan_name(database.pool, member.id), member.id)
    message, clan_name = await remove_member_from_clan(database.pool, await get_clan_name(database.pool, ctx.author.id), member.id)
    await update_nick(ctx, database.pool, member.id, await get_clan_name(database.pool, member.id))
    await ctx.respond(message.replace("%id", str(member)).replace("%c_name", clan_name))


@tanjun.with_cooldown("change_tag")
@tanjun.with_check(is_clan_owner)
@tanjun.with_str_slash_option("tag", "The new tag")
@tanjun.as_slash_command("change_tag", "Change the tag of your name")
async def change_tag_command(
        ctx: tanjun.abc.SlashContext,
        tag: str,
        database: Database = tanjun.inject(type=Database)):
    message, tag, clan_name = await change_tag_clan(database.pool, await get_clan_name(database.pool, ctx.author.id), tag)
    member = await get_clan_member(database.pool, await get_clan_name(database.pool, ctx.author.id))
    for member_id in member:
        await update_nick(ctx, database.pool, member_id, await get_clan_name(database.pool, ctx.author.id))
    await ctx.respond(message.replace("%tag", tag).replace("%c_name", clan_name))


@tanjun.with_cooldown("enable_disable_clan", error_message="You can use this command once every day")
@tanjun.with_check(is_clan_owner)
@tanjun.as_slash_command("disable_clan", "Disable the Clan")
async def disable_clan_command(
        ctx: tanjun.abc.SlashContext,
        database: Database = tanjun.inject(type=Database)):
    check = await disable_clan(database.pool, await get_clan_name(database.pool, ctx.author.id))
    if check is True:
        await ctx.respond("The Clan is now disabled and is not allowed to play any more games")
    else:
        await ctx.respond("An Error occurred while disabling the clan please talk to a staff member")


@tanjun.with_cooldown("enable_disable_clan", error_message="You can use this command once every day")
@tanjun.with_check(is_clan_owner)
@tanjun.as_slash_command("enable_clan", "Disable the Clan")
async def enable_clan_command(
        ctx: tanjun.abc.SlashContext,
        database: Database = tanjun.inject(type=Database)):
    check = await enable_clan(database.pool, await get_clan_name(database.pool, ctx.author.id))
    if check is True:
        await ctx.respond("The Clan is now enabled and is allowed to play games")
    else:
        await ctx.respond("An Error occurred while enabling the clan please talk to a staff member")


@tanjun.with_check(is_clan_owner)
@tanjun.with_bool_slash_option("confirm", "Confirm that you want to delete the clan", default=False)
@tanjun.as_slash_command("delete_clan", "Deletes YOur Clan")
async def delete_clan_command(
        ctx: tanjun.abc.SlashContext,
        confirm: bool,
        database: Database = tanjun.inject(type=Database)):
    if confirm is False:
        await ctx.respond("You have to confirm that you want to delete the clan")
        return
    member = await get_clan_member(database.pool, await get_clan_name(database.pool, ctx.author.id))
    for member_id in member:
        await update_nick(ctx, database.pool, member_id, await get_clan_name(database.pool, ctx.author.id))
    await delete_clan_role(ctx, await get_clan_name(database.pool, ctx.author.id))
    check = await delete_clan(database.pool, await get_clan_name(database.pool, ctx.author.id))

    if check is True:
        await ctx.respond("The Clan is now deleted and this action can't be undone")
    else:
        await ctx.respond("An Error occurred while deleting the clan please talk to a staff member")


clan_loader = tanjun.Component(name="clan", strict=True).load_from_scope().make_loader()
