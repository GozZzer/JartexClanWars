import hikari
import tanjun

from clanwars.database import Database, register_new_member, change_ign_member, add_alias_member, remove_alias_member
from clanwars.database.utils.clan_utils import get_clan_name
from clanwars.discord import update_nick


@tanjun.with_member_slash_option("member", "The member you want to register")
@tanjun.with_str_slash_option("ign", "Insert your Ingamename")
@tanjun.as_slash_command("force_register", "Register another user")
async def force_register_member(
        ctx: tanjun.abc.Context,
        member: hikari.InteractionMember | hikari.guilds.Member,
        ign: str,
        database: Database = tanjun.inject(type=Database)):
    message, member_id, ign = await register_new_member(database.pool, member.id, ign)
    await ctx.respond(message.replace("%name", ign).replace("%id", ctx.get_guild().get_member(member_id).mention))


@tanjun.with_member_slash_option("member", "The member you want to change the ign of")
@tanjun.with_str_slash_option("new_ign", "Insert the new Ingamename")
@tanjun.as_slash_command("force_change_ign", "Change your current ign to a new ign")
async def force_change_ign_command(
        ctx: tanjun.abc.Context,
        member: hikari.InteractionMember | hikari.guilds.Member,
        new_ign: str,
        database: Database = tanjun.inject(type=Database)):
    message, member_id, ign = await change_ign_member(database.pool, member.id, new_ign)
    await update_nick(ctx, database.pool, member.id, await get_clan_name(database.pool, member.id))
    await ctx.respond(message.replace("%ign", ign).replace("%id", ctx.get_guild().get_member(member_id).mention))


@tanjun.with_member_slash_option("member", "The member you want to add the alias to")
@tanjun.with_str_slash_option("alias", "Insert the alias you want to add the account")
@tanjun.as_slash_command("force_add_alias", "Add an alias to the list of the aliases of the member")
async def force_add_alias_command(
        ctx: tanjun.abc.Context,
        member: hikari.InteractionMember | hikari.guilds.Member,
        alias: str,
        database: Database = tanjun.inject(type=Database)):
    message, member_id, alias_now = await add_alias_member(database.pool, member.id, alias)
    await ctx.respond(message.replace("%alias", alias_now).replace("%id", str(ctx.get_guild().get_member(member_id))))


@tanjun.with_member_slash_option("member", "The member you want to remove the alias from")
@tanjun.with_str_slash_option("alias", "Insert the alias you want to remove from the account")
@tanjun.as_slash_command("force_remove_alias", "Remove an alias from the list of the aliases of the member")
async def force_remove_alias_command(
        ctx: tanjun.abc.Context,
        member: hikari.InteractionMember | hikari.guilds.Member,
        alias: str,
        database: Database = tanjun.inject(type=Database)):
    message, member_id, alias_now = await remove_alias_member(database.pool, member.id, alias)
    await ctx.respond(message.replace("%alias", alias_now).replace("%id", str(ctx.get_guild().get_member(member_id))))


staff_member_loader = tanjun.Component(name="staff.member", strict=True).load_from_scope().make_loader()
