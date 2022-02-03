from typing import Optional
import asyncio

import asyncpg
import tanjun
import hikari
from hikari import ButtonStyle

from clanwars.bot.client import ClanWarsClient
from clanwars.bot.bot import ClanWarsBot

# Create Component for this File
component = tanjun.Component()


@component.with_slash_command
@tanjun.with_str_slash_option("ign", "Type in your In-Game-Name")
@tanjun.as_slash_command("register", "Register you and set you ingamename.")
async def register(ctx: tanjun.abc.SlashContext,
                   ign: str,
                   client: ClanWarsClient = tanjun.injected(type=ClanWarsClient),
                   bot: ClanWarsBot = tanjun.injected(type=ClanWarsBot)):
    member: hikari.interactions.base_interactions.InteractionMember = ctx.member
    pool: asyncpg.pool.Pool = client.db
    try:
        await pool.execute("INSERT INTO members (user_id, ign) VALUES ($1, $2)", member.id, ign)
        try:
            await member.edit(nick=f"[] {ign}")
        except hikari.errors.ForbiddenError:
            pass
        await ctx.member.add_role(ctx.get_guild().get_role(917001261839163422))
        await ctx.respond(f"Registered yourself as: **{ign}**")
    except asyncpg.exceptions.UniqueViolationError:
        await ctx.respond(client.fast_embed(title="You are already registered",
                                            description="If you want add an alt to your account please use **/addalt**"))


@component.add_slash_command
@tanjun.with_str_slash_option("altname", "What is the name of your alt")
@tanjun.with_member_slash_option("member", "Member you want to add this alt to (Mod only)")
@tanjun.as_slash_command("addalt", "Add an alt to your account")
async def add_alt(ctx: tanjun.abc.SlashContext,
                  altname: str,
                  member: hikari.interactions.base_interactions.InteractionMember,
                  client: ClanWarsClient = tanjun.injected(type=ClanWarsClient),
                  bot: ClanWarsBot = tanjun.injected(type=ClanWarsBot)):
    author: hikari.interactions.base_interactions.InteractionMember = ctx.member
    pool: asyncpg.pool.Pool = client.db

    check = await pool.execute("UPDATE members SET other_igns = array_append(other_igns,$1) WHERE user_id=$2",
                               altname,
                               author.id)
    if check.endswith("1"):
        await ctx.respond(client.fast_embed(description=f"**{altname}** got added to your alts"))
    else:
        await ctx.respond(client.fast_embed(
            description=f"**{altname}** can`t be added to your account because you are not registered\n"
                        f"Use /register to register yourself"))


@component.add_slash_command
@tanjun.with_member_slash_option("member", "Type in the member you want to get the information about", default=None)
@tanjun.with_bool_slash_option("mod", "Show more information about the member (Mod only)", default=False)
@tanjun.as_slash_command("user_info", "Information about a specified member")
async def user_info(ctx: tanjun.abc.SlashContext,
                    mod: bool,
                    member: Optional[hikari.interactions.base_interactions.InteractionMember],
                    client: ClanWarsClient = tanjun.injected(type=ClanWarsClient),
                    bot: ClanWarsBot = tanjun.injected(type=ClanWarsBot)):
    author: hikari.interactions.base_interactions.InteractionMember = ctx.member
    pool: asyncpg.pool.Pool = client.db
    if member is None:
        member = author
    user = await pool.fetchrow("SELECT * FROM members WHERE user_id=$1", member.id)
    if user is None:
        await ctx.respond(client.fast_embed(description="The user is not registered"))
        return
    embed = hikari.embeds.Embed(
                title=f"{member}`s Account",
                description=f"ID: {member.id}",
                color=hikari.Color.from_rgb(12, 240, 11))
    embed.add_field("Name:", user["ign"])
    if user["other_igns"]:
        embed.add_field("Alts:", ", ".join(user["other_igns"]))
    else:
        embed.add_field("Alts:", "No Alts")
    if user["clan"]:
        embed.add_field("Clan:", user["clan"])
    else:
        embed.add_field("Clan:", "No Clan")
    await ctx.respond(embed)


@tanjun.as_loader
def load_component(client: ClanWarsClient):
    client.add_component(component.copy())
