#  MIT License
#
#  Copyright (c) 2022 GozZzer
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
import datetime
import hikari
import tanjun

from clanwars.utils import Database, respond, checks, send, embed, User

__all__ = [
    "clan_group",
    "create_command", "invite_command", "display_invites_command", "remove_invite_command", "accept_clan", "kick_command",
    "disband_command"
]

clan_group = tanjun.slash_command_group("clan", "Clan Commands", )


@clan_group.with_command
@tanjun.with_guild_check()
@tanjun.with_check(checks.is_not_clan_owner)
@tanjun.with_str_slash_option("name", "Set your Name of the clan")
@tanjun.with_str_slash_option("tag", "Set the Tag for the clan")
@tanjun.as_slash_command("create", "Create a clan", sort_options=False)
async def create_command(
        ctx: tanjun.SlashContext,
        name: str,
        tag: str,
        db: Database = tanjun.inject(type=Database)):
    insert = await db.insert_into("clan", name=name, tag=tag, owner_id=ctx.author.id)
    if insert is True:
        await respond(ctx, "Your clan got successfully registered", "approved")
    elif insert == "tag":
        await respond(ctx, f"The tag **{tag}** is already used", "error")
    elif insert == "name":
        await respond(ctx, f"The name **{name}** is already used", "error")
    elif isinstance(insert, Exception):
        await respond(
            ctx,
            "An unexpected error occurred",
            "unexpected_error",
            f"**Who:**{ctx.author.mention}\n**Command:**/clan create `name:{name}` `tag:{tag}`\n**Channel:**{ctx.get_channel().mention}\n{str(insert)}")


@clan_group.with_command
@tanjun.with_guild_check()
@tanjun.with_check(checks.is_clan_owner)
@tanjun.with_member_slash_option("member", "The member you want to add to your clan")
@tanjun.as_slash_command("invite", "Invite a clan member to join your clan")
async def invite_command(
        ctx: tanjun.SlashContext,
        member: hikari.InteractionMember,
        db: Database = tanjun.inject(type=Database),
        users: User = tanjun.inject(type=User)):
    if member.id == users.BOT:
        await respond(ctx, "You are not allowed to invite me to your clan", "error")
        return

    other_clan = await db.select_any("clan", member.id, "name", any="members", owner_id=ctx.author.id, deleted=False)
    if other_clan:
        await respond(ctx, f"{member.mention} is already part of {other_clan[0]['name']}", "error")
        return

    other_owner = await db.select("clan", "name", owner_id=member.id)
    if other_owner:
        await respond(ctx, f"{member.mention} is the owner  of {other_owner[0]['name']}", "error")
        return

    already_inv = await db.select_any("clan", member.id, "name", any="invites", owner_id=ctx.author.id)
    if already_inv:
        await respond(ctx, f"{member.mention} is already invited to you clan", "approved")
        return
    await db.update_append("clan", "invites", member.id, owner_id=ctx.author.id)
    clan = await db.select('clan', 'name', owner_id=ctx.author.id)
    await send(member, f"{ctx.author.mention} invited you to **{clan[0]['name']}**", "normal")

    await respond(ctx, f"{member.mention} received the clan invite", "approved")


@clan_group.with_command
@tanjun.with_guild_check()
@tanjun.with_check(checks.is_clan_owner)
@tanjun.as_slash_command("display_invites", "Shows all current Invites to your clan")
async def display_invites_command(
        ctx: tanjun.SlashContext,
        db: Database = tanjun.inject(type=Database)):
    invites = await db.select("clan", "invites", owner_id=ctx.author.id, deleted=False)
    if not invites[0]["invites"]:
        await respond(ctx, "There are currently no invites", "error")
        return
    invites = [inv for inv in invites[0]["invites"]]
    await embed(ctx,
                "Current Invites",
                "Here are all outgoing invites",
                Invites="\n".join([ctx.get_guild().get_member(inv).mention for inv in invites]))


@clan_group.with_command
@tanjun.with_check(checks.is_clan_owner)
@tanjun.with_member_slash_option("member", "The invite you want to remove")
@tanjun.as_slash_command("remove_invite", "Remove invite from your clan")
async def remove_invite_command(
        ctx: tanjun.SlashContext,
        member: hikari.InteractionMember,
        db: Database = tanjun.inject(type=Database)):
    invite = await db.select_any("clan", member.id, "name", owner_id=ctx.author.id, any="invites", deleted=False)
    if not invite:
        await respond(ctx, f"{member.mention} is not invited to your clan", "error")
        return
    await db.update_remove("clan", "invites", member.id, owner_id=ctx.author.id)
    await respond(ctx, f"{member.mention} is not invited anymore", "approved")


@clan_group.with_command
@tanjun.with_str_slash_option("clan", "The name of the clan you want to join")
@tanjun.as_slash_command("accept", "Accept a clan invite")
async def accept_clan(
        ctx: tanjun.SlashContext,
        clan: str,
        db: Database = tanjun.inject(type=Database),
        client: tanjun.Client = tanjun.inject(type=tanjun.Client)):
    check_invite = await db.select_any("clan", ctx.author.id, "owner_id", any="invites", name=clan, deleted=False)
    if not check_invite:
        await respond(ctx, f"You are not invited to **{clan}**")
        return

    await db.update_append("clan", "members", ctx.author.id, name=clan)
    await db.update_remove("clan", "invites", ctx.author.id, name=clan)
    try:
        guild = await ctx.get_guild()
        owner = await guild.get_member(check_invite[0]["owner_id"])
    except TypeError:
        owner = await client.rest.fetch_member(894305669396697089, check_invite[0]["owner_id"])
    await send(owner, f"{ctx.author} accepted your clan invite")
    await respond(ctx, f"You are now a member of **{clan}**")


@clan_group.with_command
@tanjun.with_check(checks.is_clan_owner)
@tanjun.with_member_slash_option("member", "The member you want to kick")
@tanjun.as_slash_command("kick", "Kicks a member of your clan")
async def kick_command(
        ctx: tanjun.SlashContext,
        member: hikari.InteractionMember,
        db: Database = tanjun.inject(type=Database)):
    check_part_of = await db.select_any("clan", member.id, "name", any="members", owner_id=ctx.author.id, deleted=False)
    if not check_part_of:
        await respond(ctx, f"{member.mention} is not part of your clan", "error")
        return

    owner_clan = await db.select("clan", "name", owner_id=ctx.author.id)
    if owner_clan[0]["name"] != check_part_of[0]["name"]:
        await respond(ctx, f"{member.mention} is not part of your clan", "error")
        return

    await db.update_remove("clan", "members", member.id, owner_id=ctx.author.id)
    await db.update_append("clan", "was_member", member.id, owner_id=ctx.author.id)
    await respond(ctx, f"{member.mention} has been kicked out of your clan", "approved")


@clan_group.with_command
@tanjun.with_check(checks.is_clan_owner)
@tanjun.with_bool_slash_option("approve", "Do you really want to disband this clan", default=False)
@tanjun.as_slash_command("disband", "Disbands your clan (This can't be undone)")
async def disband_command(
        ctx: tanjun.SlashContext,
        approve: bool,
        db: Database = tanjun.inject(type=Database)):
    if approve is False:
        await respond(ctx, "You have to approve that you want to disband the clan", "error")
        return
    data = await db.select("clan", "name", "tag", owner_id=ctx.author.id, deleted=False)
    print(data)
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    await db.update_values(
        "clan",
        v_deleted=True,
        v_name=f'd_{now.strftime("%d-%m-%Y|%H:%M:%S.%f")}_{data[0]["row"][0]}',
        v_tag=f'd_{now.strftime("%d-%m-%Y|%H:%M:%S.%f")}_{data[0]["row"][1]}',
        owner_id=ctx.author.id,
        deleted=False)
    await respond(ctx, "Your clan has been disband", "approved")

clan_loader = tanjun.Component(name="clan", strict=True).load_from_scope().make_loader()
