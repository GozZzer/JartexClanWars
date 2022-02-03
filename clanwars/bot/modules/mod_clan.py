import asyncio.exceptions
from typing import Optional

import asyncpg
import hikari
import tanjun
from hikari import ButtonStyle

from clanwars.bot.client import ClanWarsClient
from clanwars.bot.bot import ClanWarsBot
from clanwars.bot.utils.checks import can_register, is_clan_owner, can_register_listener, is_admin

component = tanjun.Component()


@component.with_slash_command
@tanjun.with_check(can_register)
@tanjun.with_guild_check(error_message="You are only allowed to use this Command in a guild")
@tanjun.with_member_slash_option("owner", "Insert the Clan Member")
@tanjun.with_str_slash_option("clanname", "Insert the Clan Name")
@tanjun.as_slash_command("force_clan_register", "Register a Clan (Mod Only)")
async def force_clan_register(
        ctx: tanjun.abc.SlashContext,
        owner: hikari.interactions.base_interactions.InteractionMember,
        clanname: str,
        client: ClanWarsClient = tanjun.injected(type=ClanWarsClient),
        bot: ClanWarsBot = tanjun.injected(type=ClanWarsBot)):
    author: hikari.interactions.base_interactions.InteractionMember = ctx.member
    pool: asyncpg.pool.Pool = client.db
    try:
        await pool.execute(
            "INSERT INTO clans (owner_id, clan_name, accepted) VALUES ($1, $2, $3)",
            owner.id,
            clanname,
            True
        )
    except asyncpg.exceptions.UniqueViolationError:
        clan = await pool.fetchrow("SELECT * FROM clans WHERE owner_id=$1", owner.id)
        if clan["deleted"] is True:
            await ctx.respond(client.fast_embed(
                title="Your Clan is deleted",
                description="If you want to reactivate your clan user `/reactivate`"
            ))
        elif clan["enabled"] is False:
            await ctx.respond(client.fast_embed(
                title="Your Clan is disabled",
                description="If you don't know why your Clan got disabled ask a staff-member"))
        else:
            await ctx.respond(client.fast_embed("This Clan-Name is already registered"))
        return
    registered_channel = ctx.get_guild().get_channel(894322877321588766)
    clan = await pool.fetchrow("SELECT * FROM clans WHERE clan_name=$1", clanname)
    role = await ctx.rest.create_role(
        ctx.get_guild(),
        name=clanname,
        reason=f"{author} force registered the clan-submission")
    await pool.execute("UPDATE clans SET role=$1 WHERE clan_name=$2", role.id, clanname)
    await ctx.get_guild().get_member(clan["owner_id"]).add_role(
        role,
        reason=f"{author} force registered the clan-submission")
    await registered_channel.send(
        content=ctx.get_guild().get_member(clan["owner_id"]).mention,
        embed=client.fast_embed(
            description=f"__{clanname}__ got registered by {author.mention}",
            color=hikari.Color.from_rgb(10, 255, 10)
        )
    )
    await ctx.respond(client.fast_embed(description=f"Force Registered {clanname}"))


@component.with_slash_command
@tanjun.with_check(is_admin)
@tanjun.with_guild_check(error_message="You are only allowed to use this Command in a guild")
@tanjun.with_str_slash_option("clanname", "Type in the name of the clan you want to force-delete", default=None)
@tanjun.with_member_slash_option("owner", "Type in the name of the owner of the clan you want to force-delete",
                                 default=None)
@tanjun.as_slash_command("force_clan_delete", "Delete a Clan (Mod Only)")
async def force_clan_delete(
        ctx: tanjun.abc.SlashContext,
        owner: Optional[hikari.interactions.base_interactions.InteractionMember],
        clanname: Optional[str],
        client: ClanWarsClient = tanjun.injected(type=ClanWarsClient),
        bot: ClanWarsBot = tanjun.injected(type=ClanWarsBot)):
    if owner is None and clanname is None:
        await ctx.respond(client.fast_embed(description="You need to insert at leas one thing a clanname or a owner"))
        return
    author: hikari.interactions.base_interactions.InteractionMember = ctx.member
    pool: asyncpg.pool.Pool = client.db
    if owner is not None:
        clan = await pool.fetchrow("SELECT * FROM clans WHERE owner_id=$1", owner.id)
        if clan is None:
            await ctx.respond(client.fast_embed(f"{owner.mention} does not own a clan"))
            return
    if clanname is not None:
        clan = await pool.fetchrow("SELECT * FROM clans WHERE clan_name=$1", clanname)
        if clan is None:
            await ctx.respond(client.fast_embed(description=f"The clan {clanname} does not exist"))
            return

    guild = ctx.get_guild()
    role = [role for role in await ctx.get_guild().fetch_roles() if role.id == clan["role"]][0]

    if clan["members"]:
        members = clan["members"] + [owner.id]
    else:
        members = [owner.id]
    for member_id in members:
        member_db = await pool.fetchrow("SELECT * FROM members WHERE user_id=$1", member_id)
        member = guild.get_member(member_id)
        await pool.execute("UPDATE members SET clan=$1 WHERE user_id=$2", None, member_id)
        await member.remove_role(role, reason=f"{clan['clan_name']} got deleted by {owner}")
        try:
            await member.edit(nick=f"[] {member_db['ign']}")
        except hikari.errors.ForbiddenError:
            pass
    await pool.execute("UPDATE clans SET deleted=$1, role=$2 WHERE owner_id=$3", True, None, owner.id)
    await ctx.rest.delete_role(guild, role)
    await ctx.respond(client.fast_embed(description="The Clan got deleted"))
    channel = guild.get_channel(894322877321588766)
    await channel.send(client.fast_embed(description=f"__{clan['clan_name']}__ got deleted by {author.mention}",
                                         color=hikari.Color.from_rgb(255, 10, 10)))


@tanjun.as_loader
def load_component(client: ClanWarsClient):
    client.add_component(component.copy())
