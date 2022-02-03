import hikari
import tanjun

from clanwars.database import Database, new_register_clan, add_member_to_clan, remove_member_from_clan, change_tag_clan
from clanwars.database.utils.clan_utils import set_role_id, get_clan_name, get_clan_member, disable_clan, enable_clan, delete_clan
from clanwars.discord import create_clan_role, add_clan_role, update_nick, remove_clan_role, delete_clan_role


@tanjun.with_member_slash_option("owner", "The owner of the clan")
@tanjun.with_str_slash_option("clan_name", "The name of the clan")
@tanjun.as_slash_command("force_register_clan", "Register the clan for the owner")
async def force_register_clan_command(
        ctx: tanjun.abc.Context,
        owner: hikari.InteractionMember | hikari.guilds.Member,
        clan_name: str,
        database: Database = tanjun.inject(type=Database)):
    message, value = await new_register_clan(database.pool, clan_name, owner.id)
    role = await create_clan_role(ctx, clan_name)
    await set_role_id(database.pool, role.id, clan_name)
    await add_clan_role(ctx, clan_name, owner.id)
    await update_nick(ctx, database.pool, owner.id, clan_name)
    await ctx.respond(message.replace("%id", str(owner)).replace("%c_name", value))


@tanjun.with_str_slash_option("clan_name", "The name of the clan to add the member to", default=None)
@tanjun.with_member_slash_option("clan_owner", "The owner of the clan", default=None)
@tanjun.with_member_slash_option("member", "The member you want to add to your clan")
@tanjun.as_slash_command("force_add_member", "Add a member to your clan")
async def force_add_member_command(
        ctx: tanjun.abc.Context,
        clan_name: str,
        clan_owner: hikari.InteractionMember | hikari.guilds.Member,
        member: hikari.InteractionMember | hikari.guilds.Member,
        database: Database = tanjun.inject(type=Database)):
    if clan_name is None and clan_owner is None:
        await ctx.respond("You need to define a clan_owner or a clan_name")
        return
    if clan_name is None:
        clan_name = await get_clan_name(database.pool, clan_owner.id)
        if not clan_name:
            await ctx.respond(f"{clan_owner} does not own a clan")
            return
    message, clan_name = await add_member_to_clan(database.pool, clan_name, member.id)
    await add_clan_role(ctx, clan_name, member.id)
    await update_nick(ctx, database.pool, member.id, await get_clan_name(database.pool, member.id))
    await ctx.respond(message.replace("%id", str(member)).replace("%c_name", clan_name))
    

@tanjun.with_str_slash_option("clan_name", "The name of the clan to add the member to", default=None)
@tanjun.with_member_slash_option("clan_owner", "The owner of the clan", default=None)
@tanjun.with_member_slash_option("member", "The member you want to add to your clan")
@tanjun.as_slash_command("force_remove_member", "Add a member to your clan")
async def force_remove_member_command(
        ctx: tanjun.abc.Context,
        clan_name: str,
        clan_owner: hikari.InteractionMember | hikari.guilds.Member,
        member: hikari.InteractionMember | hikari.guilds.Member,
        database: Database = tanjun.inject(type=Database)):
    if clan_name is None and clan_owner is None:
        await ctx.respond("You need to define a clan_owner or a clan_name")
        return
    if clan_name is None:
        clan_name = await get_clan_name(database.pool, clan_owner.id)
        if not clan_name:
            await ctx.respond(f"{clan_owner} does not own a clan")
            return
    await remove_clan_role(ctx, clan_name, member.id)
    message, clan_name = await remove_member_from_clan(database.pool, clan_name, member.id)
    await update_nick(ctx, database.pool, member.id, await get_clan_name(database.pool, member.id))
    await ctx.respond(message.replace("%id", str(member)).replace("%c_name", clan_name))
    

@tanjun.with_str_slash_option("clan_name", "The name of the clan to add the member to", default=None)
@tanjun.with_member_slash_option("clan_owner", "The owner of the clan", default=None)
@tanjun.with_str_slash_option("tag", "The new tag")
@tanjun.as_slash_command("force_change_tag", "Change the tag of your name")
async def force_change_tag_command(
        ctx: tanjun.abc.Context,
        clan_name: str,
        clan_owner: hikari.InteractionMember | hikari.guilds.Member,
        tag: str,
        database: Database = tanjun.inject(type=Database)):
    if clan_name is None and clan_owner is None:
        await ctx.respond("You need to define a clan_owner or a clan_name")
        return
    if clan_name is None:
        clan_name = await get_clan_name(database.pool, clan_owner.id)
        if not clan_name:
            await ctx.respond(f"{clan_owner} does not own a clan")
            return
    message, new_tag, clan_name = await change_tag_clan(database.pool, clan_name, tag)
    member = await get_clan_member(database.pool, clan_name)
    if member:
        member = member + [clan_owner.id]
    else:
        member = [clan_owner.id]
    for member_id in member:
        await update_nick(ctx, database.pool, member_id, clan_name)
    await ctx.respond(message.replace("%tag", new_tag).replace("%c_name", clan_name))
    

@tanjun.with_str_slash_option("clan_name", "The name of the clan to add the member to", default=None)
@tanjun.with_member_slash_option("clan_owner", "The owner of the clan", default=None)
@tanjun.as_slash_command("force_disable_clan", "Disable the Clan")
async def force_disable_clan_command(
        ctx: tanjun.abc.Context,
        clan_name: str,
        clan_owner: hikari.InteractionMember | hikari.guilds.Member,
        database: Database = tanjun.inject(type=Database)):
    if clan_name is None and clan_owner is None:
        await ctx.respond("You need to define a clan_owner or a clan_name")
        return
    if clan_name is None:
        clan_name = await get_clan_name(database.pool, clan_owner.id)
        if not clan_name:
            await ctx.respond(f"{clan_owner} does not own a clan")
            return
    check = await disable_clan(database.pool, clan_name)
    if check is True:
        await ctx.respond("The Clan is now disabled and is not allowed to play any more games")
    else:
        await ctx.respond("An Error occurred while disabling the clan please talk to a staff member")


@tanjun.with_str_slash_option("clan_name", "The name of the clan to add the member to", default=None)
@tanjun.with_member_slash_option("clan_owner", "The owner of the clan", default=None)
@tanjun.as_slash_command("force_enable_clan", "Disable the Clan")
async def force_enable_clan_command(
        ctx: tanjun.abc.Context,
        clan_name: str,
        clan_owner: hikari.InteractionMember | hikari.guilds.Member,
        database: Database = tanjun.inject(type=Database)):
    if clan_name is None and clan_owner is None:
        await ctx.respond("You need to define a clan_owner or a clan_name")
        return
    if clan_name is None:
        clan_name = await get_clan_name(database.pool, clan_owner.id)
        if not clan_name:
            await ctx.respond(f"{clan_owner} does not own a clan")
            return
    check = await enable_clan(database.pool, clan_name)
    if check is True:
        await ctx.respond("The Clan is now enabled and is allowed to play games")
    else:
        await ctx.respond("An Error occurred while enabling the clan please talk to a staff member")


@tanjun.with_str_slash_option("clan_name", "The name of the clan to add the member to", default=None)
@tanjun.with_member_slash_option("clan_owner", "The owner of the clan", default=None)
@tanjun.with_bool_slash_option("confirm", "Confirm that you want to delete the clan", default=False)
@tanjun.as_slash_command("force_delete_clan", "Deletes YOur Clan")
async def force_delete_clan_command(
        ctx: tanjun.abc.Context,
        clan_name: str,
        clan_owner: hikari.InteractionMember | hikari.guilds.Member,
        confirm: bool,
        database: Database = tanjun.inject(type=Database)):
    if confirm is False:
        await ctx.respond("You have to confirm that you want to delete the clan")
        return
    if clan_name is None and clan_owner is None:
        await ctx.respond("You need to define a clan_owner or a clan_name")
        return
    if clan_name is None:
        clan_name = await get_clan_name(database.pool, clan_owner.id)
        if not clan_name:
            await ctx.respond(f"{clan_owner} does not own a clan")
            return
    
    member = await get_clan_member(database.pool, clan_name)
    if member:
        member = member + [clan_owner.id]
    else:
        member = [clan_owner.id]
    await delete_clan_role(ctx, clan_name)
    check = await delete_clan(database.pool, clan_name)
    for member_id in member:
        await update_nick(ctx, database.pool, member_id)

    if check is True:
        await ctx.respond("The Clan is now deleted and this action can't be undone")
    else:
        await ctx.respond("An Error occurred while deleting the clan please talk to a staff member")


staff_clan_loader = tanjun.Component(name="staff.clan", strict=True).load_from_scope().make_loader()