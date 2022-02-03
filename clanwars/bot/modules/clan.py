import asyncio.exceptions

import asyncpg
import hikari
import tanjun
from hikari import ButtonStyle

from clanwars.bot.client import ClanWarsClient
from clanwars.bot.bot import ClanWarsBot
from clanwars.bot.utils.checks import is_clan_owner, can_register_listener, was_clan_owner
from clanwars.bot.utils.database.member import fetch_member
from clanwars.bot.utils.database.objects import Member
component = tanjun.Component()


@component.with_slash_command
@tanjun.with_guild_check(error_message="You are only allowed to use this Command in a guild")
@tanjun.with_str_slash_option("clanname", "Insert the Guild Name which you want to register.")
@tanjun.with_int_slash_option("membercount", "How many Members are in your Clan? (Include yourself)")
@tanjun.as_slash_command("register_clan",
                         "When you own a clan register it here and allow your clan to play so Clan Wars")
async def register_clan(
        ctx: tanjun.abc.SlashContext,
        clanname: str = None,
        membercount: int = None,
        client: ClanWarsClient = tanjun.injected(type=ClanWarsClient),
        bot: ClanWarsBot = tanjun.injected(type=ClanWarsBot)):
    owner: hikari.interactions.base_interactions.InteractionMember = ctx.member
    pool: asyncpg.pool.Pool = client.db
    member_db = await pool.execute("SELECT * FROM members WHERE user_id=$1", owner.id)
    if member_db is None:
        await ctx.respond(
            client.fast_embed(title="You are not registered", description="Register yourself using `/register`")
        )
        return

    if membercount < 3:
        await ctx.respond(
            client.fast_embed(description="You need more than 3 members to join ClanWars.")
        )
        return

    else:
        try:
            await pool.execute(
                "INSERT INTO clans (owner_id, clan_name, accepted) VALUES ($1, $2, $3)",
                owner.id,
                clanname,
                False
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
        if ctx.has_responded:
            await ctx.edit_last_response(
                embed=client.fast_embed(description="Please send a screenshot of your Clan-Members overview.")
            )
        else:
            await ctx.respond(
                embed=client.fast_embed(description="Please send a screenshot of your Clan-Members overview.")
            )
        while True:
            try:
                event: hikari.events.message_events.GuildMessageCreateEvent = await bot.wait_for(
                    hikari.events.message_events.GuildMessageCreateEvent,
                    timeout=60
                )
                message = event.message
                if message.author.id == owner.id:
                    if message.attachments is None:
                        await ctx.edit_last_response(
                            client.fast_embed("You didn't send a picture in the chat (Try again)")
                        )
                    else:
                        attachments = message.attachments
                        if not attachments[0].media_type.startswith("image"):
                            await ctx.edit_last_response(
                                client.fast_embed("Please insert a Image.")
                            )
                            continue
                        else:
                            image = await attachments[0].read()
                            await message.delete()
                        break
                else:
                    continue
            except asyncio.exceptions.TimeoutError:
                await ctx.edit_last_response(
                    client.fast_embed("I stopped waiting for a Message")
                )
                return
        await pool.execute(
            "UPDATE clans SET proof=$1",
            image
        )
        row = ctx.rest.build_action_row()
        (
            row.add_button(ButtonStyle.SECONDARY, "rc___" + clanname)
                .set_label("Register")
                .set_emoji("✅")
                .add_to_container()
        )
        guild = await ctx.fetch_guild()
        register_channel = guild.get_channel(895041120285884446)
        await register_channel.send(f"A new clan got registered(**{clanname}**)", components=[row, ])
        await ctx.edit_last_response(
            client.fast_embed("Thank You for registering your Clan\n"
                              "Wait until a staff member accepts your submission.")
        )


@component.with_slash_command
@tanjun.with_check(is_clan_owner)
@tanjun.with_bool_slash_option("confirm", "Do You really want to delete this Clan", default=False)
@tanjun.as_slash_command("delete_clan", "Delete your Clan")
async def delete_clan(
        ctx: tanjun.abc.SlashContext,
        confirm: bool = False,
        client: ClanWarsClient = tanjun.injected(type=ClanWarsClient),
        bot: ClanWarsBot = tanjun.injected(type=ClanWarsBot)):
    owner: hikari.interactions.base_interactions.InteractionMember = ctx.member
    pool: asyncpg.pool.Pool = client.db
    if not confirm:
        await ctx.respond(client.fast_embed(description="You haven't confirmed that you want to delete your clan"))
        return

    clan = await pool.fetchrow("SELECT * FROM clans WHERE owner_id=$1", owner.id)
    guild = ctx.get_guild()
    role = [role for role in await ctx.get_guild().fetch_roles() if role.id == clan["role"]][0]

    if clan["members"]:
        members = clan["members"] + [owner.id]
    else:
        members = [owner.id]
    for member_id in members:
        member_db = await pool.fetchrow("SELECT * FROM members WHERE user_id=$1", member_id)
        member = guild.get_member(member_id)
        await pool.execute("UPDATE members SET clan=$1 WHERE user_id=$2", None,  member_id)
        await member.remove_role(role, reason=f"{clan['clan_name']} got deleted by {owner}")
        try:
            await member.edit(nick=f"[] {member_db['ign']}")
        except hikari.errors.ForbiddenError:
            pass
    await pool.execute("UPDATE clans SET deleted=$1, role=$2 WHERE owner_id=$3", True, None, owner.id)
    await ctx.rest.delete_role(guild, role)
    await ctx.respond(client.fast_embed(description="The Clan got deleted"))
    channel = guild.get_channel(894322877321588766)
    await channel.send(client.fast_embed(description=f"__{clan['clan_name']}__ got deleted by {owner.mention}",
                                         color=hikari.Color.from_rgb(255, 10, 10)))


@component.with_slash_command
@tanjun.with_check(is_clan_owner)
@tanjun.with_guild_check(error_message="You are only allowed to use this Command in a guild")
@tanjun.with_member_slash_option("member", "Insert the member you want to add to you clan")
@tanjun.as_slash_command("add_member",
                         "Add members to your clan to play Clan Wars")
async def add_member(
        ctx: tanjun.abc.SlashContext,
        member: hikari.interactions.base_interactions.InteractionMember,
        client: ClanWarsClient = tanjun.injected(type=ClanWarsClient),
        bot: ClanWarsBot = tanjun.injected(type=ClanWarsBot)):
    author: hikari.interactions.base_interactions.InteractionMember = ctx.member
    pool: asyncpg.pool.Pool = client.db
    member_db = await pool.fetchrow("SELECT * FROM members WHERE user_id=$1", member.id)
    if member_db is None:
        await ctx.respond(client.fast_embed(description=f"{member.mention} is not registered!!\n"
                                                        f"Tell your Clan-Member that he should register using /register"))
        return
    clan = await pool.fetchrow("SELECT * FROM clans WHERE owner_id=$1", author.id)
    if clan is None:
        await ctx.respond(client.fast_embed(description=f"Your Clan is not registered!!\n"
                                                        f"Register your Clan using /registerclan"))
        return
    if clan["members"] is not None:
        if member.id in clan["members"]:
            await ctx.respond(client.fast_embed(description=f"{member.mention} is already added to you clan."))
            return
    if member_db["clan"] is not None:
        await ctx.respond(client.fast_embed(description=f"{member.mention} is already in another Clan"))
        return
    await pool.execute("UPDATE clans SET members = array_append(members, $1) WHERE clan_name=$2",
                       member.id,
                       clan["clan_name"])
    await pool.execute("UPDATE members SET clan=$2 WHERE user_id=$1", member.id, clan["clan_name"])
    role = [role for role in await ctx.get_guild().fetch_roles() if role.id == clan["role"]][0]
    await member.add_role(role, reason=f"{author} added {member} to the clan {clan['clan_name']}")
    try:
        await member.edit(nick=f"[{clan['clan_name']}] {member_db['ign']}")
    except hikari.errors.ForbiddenError:
        pass
    await ctx.respond(client.fast_embed(description=f"{member.mention} got added to your Clan"))


@component.with_slash_command
@tanjun.with_check(is_clan_owner)
@tanjun.with_guild_check(error_message="You are only allowed to use this Command in a guild")
@tanjun.with_member_slash_option("member", "Insert the member you want to add to you clan")
@tanjun.as_slash_command("remove_member",
                         "Remove members from your Clan")
async def remove_member(
        ctx: tanjun.abc.SlashContext,
        member: hikari.interactions.base_interactions.InteractionMember,
        client: ClanWarsClient = tanjun.injected(type=ClanWarsClient),
        bot: ClanWarsBot = tanjun.injected(type=ClanWarsBot)):
    author: hikari.interactions.base_interactions.InteractionMember = ctx.member
    pool: asyncpg.pool.Pool = client.db
    if member == author:
        await ctx.respond(client.fast_embed(description=f"You cannot remove yourself from your Clan!"))
        return
    member_db = await pool.fetchrow("SELECT * FROM members WHERE user_id=$1", member.id)
    if member_db is None:
        await ctx.respond(client.fast_embed(description=f"{member.mention} is not registered!!\n"
                                                        f"Tell your Clan-Member that he should register using /register"))
        return
    clan = await pool.fetchrow("SELECT * FROM clans WHERE owner_id=$1", author.id)
    if clan is None:
        await ctx.respond(client.fast_embed(description=f"Your clan is not registered!!\n"
                                                        f"Register your clan using /registerclan"))
        return
    if clan["members"] is not None:
        if member.id not in clan["members"]:
            await ctx.respond(client.fast_embed(description=f"{member.mention} is not in your clan."))
            return
    if member_db["clan"] is None:
        await ctx.respond(client.fast_embed(description=f"{member.mention} is not in any clan"))
        return
    await pool.execute("UPDATE clans SET members = array_remove(members, $1) WHERE clan_name=$2",
                       member.id,
                       clan["clan_name"])
    await pool.execute("UPDATE members SET clan=$2 WHERE user_id=$1", member.id, None)
    role = [role for role in await ctx.get_guild().fetch_roles() if role.id == clan["role"]][0]
    await member.remove_role(role, reason=f"{author} removed {member} from the clan {clan['clan_name']}")
    await member.edit(nick=f"[] {member_db['ign']}")
    await ctx.respond(client.fast_embed(description=f"{member.mention} got removed from your Clan"))


@component.with_slash_command
@tanjun.with_check(was_clan_owner)
@tanjun.with_guild_check(error_message="You are only allowed to use this Command in a guild")
@tanjun.with_str_slash_option("clanname", "Insert the name of the clan you want to reactivate")
@tanjun.as_slash_command("reactivate", "Reactivate your Clan")
async def reactivate(
        ctx: tanjun.abc.SlashContext,
        clanname: str,
        client: ClanWarsClient = tanjun.injected(type=ClanWarsClient),
        bot: ClanWarsBot = tanjun.injected(type=ClanWarsBot)):
    author: hikari.interactions.base_interactions.InteractionMember = ctx.member
    pool: asyncpg.pool.Pool = client.db
    clan = await pool.fetchrow("SELECT * FROM clans WHERE clan_name=$1", clanname)
    if clan is None:
        await ctx.respond(client.fast_embed(description=f"You haven't ever owned a clan named {clanname}"))
        return
    if clan["deleted"] is False:
        await ctx.respond(client.fast_embed(description=f"Your clan named {clanname} is not deleted."))
        return
    await pool.execute("UPDATE clans SET deleted=$1 WHERE clan_name=$2", False, clanname)
    guild = ctx.get_guild()

    roles = [role for role in await ctx.get_guild().fetch_roles() if role.id == clan["role"]]
    if not roles:
        role = await ctx.rest.create_role(
            guild,
            name=clanname,
            reason=f"{author} reactivated {clanname}")
    else:
        role = roles[0]
    owner = guild.get_member(clan["owner_id"])
    if clan["members"]:
        members = clan["members"] + [owner.id]
    else:
        members = [owner.id]
    already_clan = []
    for member_id in members:
        member_db = await pool.fetchrow("SELECT * FROM members WHERE user_id=$1", member_id)
        member = guild.get_member(member_id)
        if member_db["clan"] is not None:
            already_clan.append(member.mention)
            await pool.execute("UPDATE clans SET members=array_remove(members, $1)", member.id)
        else:
            await pool.execute("UPDATE members SET clan=$1 WHERE user_id=$2", clan["clan_name"], member_id)
            await member.add_role(role, reason=f"{clan['clan_name']} got reactivated by {owner}")
            try:
                await member.edit(nick=f"[{clan['clan_name']}] {member_db['ign']}")
            except hikari.errors.ForbiddenError:
                pass
    await pool.execute("UPDATE clans SET deleted=$1, role=$2 WHERE owner_id=$3", False, role.id, owner.id)
    if already_clan:
        await ctx.respond(client.fast_embed(title="The Clan got reactivated",
                                            description=f"I could not add {', '.join(already_clan)}"))
    else:
        await ctx.respond(client.fast_embed(title="The Clan got reactivated"))
    channel = guild.get_channel(894322877321588766)
    await channel.send(client.fast_embed(description=f"__{clan['clan_name']}__ got reactivated by {owner.mention}",
                                         color=hikari.Color.from_rgb(10, 255, 10)))


@component.with_listener(hikari.events.interaction_events.InteractionCreateEvent)
async def on_interaction_create_event(event: hikari.events.interaction_events.InteractionCreateEvent,
                                      client: ClanWarsClient = tanjun.injected(type=ClanWarsClient),
                                      bot: ClanWarsBot = tanjun.injected(type=ClanWarsBot)):
    interaction = event.interaction
    if isinstance(interaction, hikari.ComponentInteraction) and interaction.custom_id.startswith("rc___"):
        await interaction.create_initial_response(5)

        clanname = interaction.custom_id[3:]
        pool: asyncpg.pool.Pool = event.app.db
        check = await can_register_listener(pool, interaction.member)
        if isinstance(check, str):
            msg = await interaction.get_channel().send(check)
            await asyncio.sleep(5)
            await msg.delete()
            return
        clan = await pool.fetchrow("SELECT * FROM clans WHERE clan_name=$1", clanname)
        message = interaction.message
        await message.delete()
        guild = await interaction.fetch_guild()
        channel = await interaction.fetch_channel()
        owner = guild.get_member(clan["owner_id"])

        embed = hikari.Embed(
            title=f"__{clan['clan_name']}__'s Clan-Submission",
            description=f"Created by {owner.mention}",
            colour=hikari.Color.from_rgb(0, 255, 100)
        )
        embed.set_thumbnail(clan["proof"])
        embed.set_footer(
            text=f"{interaction.member} is working on this submission...",
            icon=interaction.member.avatar_url
        )
        row = event.app.rest.build_action_row()
        (
            row.add_button(ButtonStyle.SECONDARY, "ac___" + clanname)
               .set_label("Accept")
               .set_emoji("✅")
               .add_to_container()
        )
        await channel.send(embed=embed, components=[row, ])
        await interaction.delete_initial_response()
    elif isinstance(interaction, hikari.ComponentInteraction) and interaction.custom_id.startswith("ac___"):
        await interaction.create_initial_response(5)
        registered_channel = interaction.get_guild().get_channel(894322877321588766)
        message = interaction.message
        clanname = interaction.custom_id[5:]

        pool: asyncpg.pool.Pool = event.app.db
        check = await can_register_listener(pool, interaction.member)
        if isinstance(check, str):
            msg = await interaction.get_channel().send(check)
            await asyncio.sleep(5)
            await msg.delete()
            return
        clan = await pool.fetchrow("SELECT * FROM clans WHERE clan_name=$1", clanname)
        role = await event.app.rest.create_role(
            interaction.get_guild(),
            name=clanname,
            reason=f"{interaction.member} accepted the submission")
        await interaction.get_guild().get_member(clan["owner_id"]).add_role(
            role,
            reason=f"{interaction.member} accepted the submission")
        await registered_channel.send(
            content=interaction.get_guild().get_member(clan["owner_id"]).mention,
            embed=hikari.Embed(
                description=f"__{clanname}__'s Submission got accepted by {interaction.member.mention}",
                color=hikari.Color.from_rgb(10, 255, 10)
            )
        )
        await interaction.delete_initial_response()
        await message.delete()
    else:
        pass


@tanjun.as_loader
def load_component(client: ClanWarsClient):
    client.add_component(component.copy())
