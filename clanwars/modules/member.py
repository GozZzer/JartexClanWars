import tanjun


from clanwars.database import Database, register_new_member, change_ign_member, add_alias_member, remove_alias_member
from clanwars.database.utils.clan_utils import get_clan_name
from clanwars.discord import update_nick


@tanjun.with_str_slash_option("ign", "Insert your Ingamename")
@tanjun.as_slash_command("register", "Register you to join clans and play games")
async def register_member(
        ctx: tanjun.abc.SlashContext,
        ign: str,
        database: Database = tanjun.inject(type=Database)):
    message, member_id, ign = await register_new_member(database.pool, ctx.author.id, ign)
    await ctx.respond(message.replace("%name", ign).replace("%id", ctx.get_guild().get_member(member_id).mention))


@tanjun.with_str_slash_option("new_ign", "Insert the new Ingamename")
@tanjun.as_slash_command("change_ign", "Change your current ign to a new ign")
async def change_ign_command(
        ctx: tanjun.abc.SlashContext,
        new_ign: str,
        database: Database = tanjun.inject(type=Database)):
    message, member_id, ign = await change_ign_member(database.pool, ctx.author.id, new_ign)
    await update_nick(ctx, database.pool, ctx.author.id, await get_clan_name(database.pool, ctx.author.id))
    await ctx.respond(message.replace("%ign", ign).replace("%id", ctx.get_guild().get_member(member_id).mention))


@tanjun.with_str_slash_option("alias", "Insert the alias you want to add to your account")
@tanjun.as_slash_command("add_alias", "Add an alias to the list of your aliases")
async def add_alias_command(
        ctx: tanjun.abc.SlashContext,
        alias: str,
        database: Database = tanjun.inject(type=Database)):
    message, member_id, alias_now = await add_alias_member(database.pool, ctx.author.id, alias)
    await ctx.respond(message.replace("%alias", alias_now).replace("%id", ctx.get_guild().get_member(member_id).mention))


@tanjun.with_str_slash_option("alias", "Insert the alias you want to remove from your account")
@tanjun.as_slash_command("remove_alias", "Remove an alias from the list of your aliases")
async def remove_alias_command(
        ctx: tanjun.abc.SlashContext,
        alias: str,
        database: Database = tanjun.inject(type=Database)):
    message, member_id, alias_now = await remove_alias_member(database.pool, ctx.author.id, alias)
    await ctx.respond(message.replace("%alias", alias_now).replace("%id", ctx.get_guild().get_member(member_id).mention))


member_loader = tanjun.Component(name="member", strict=True).load_from_scope().make_loader()
