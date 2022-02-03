from typing import Optional

import asyncpg
import tanjun
import hikari
from hikari import ButtonStyle

from clanwars.bot.client import ClanWarsClient
from clanwars.bot.bot import ClanWarsBot
from clanwars.bot.utils.checks import is_admin

component = tanjun.Component()

EMBED_MENU = {
    "⬅️": {"title": "Back", "style": ButtonStyle.PRIMARY},
    "❌": {"title": "Exit", "style": ButtonStyle.DANGER},
    "➡️": {"title": "Next", "style": ButtonStyle.PRIMARY}
}

PERMISSIONS = {
    "admin": {
        "description": "Is allowed to do anything.",
        "id": 901433675206492200
    },
    "register": {
        "description": "Is allowed to accept Clan Suggestions",
        "id": 904792047876194334
    },
    "score": {
        "description": "Is allowed to score Games",
        "id": 904792025189208105
    }
}


@component.with_slash_command
@tanjun.with_str_slash_option(
    "option",
    "What type of staff is online at the moment",
    choices=[key for key in PERMISSIONS],
    default=None)
@tanjun.as_slash_command("staff", "See which Staff is available at the moment.")
async def staff(
        ctx: tanjun.abc.SlashContext,
        option: Optional[str],
        client: ClanWarsClient = tanjun.injected(type=ClanWarsClient),
        bot: ClanWarsBot = tanjun.injected(type=ClanWarsBot)):
    owner: hikari.interactions.base_interactions.InteractionMember = ctx.member
    pool: asyncpg.pool.Pool = client.db
    if option:
        execute = f"SELECT * FROM staff WHERE available=True AND {option}=True"
        staff = await pool.fetch(execute)
    else:
        staff = await pool.fetch("SELECT * FROM staff WHERE available=True")
    if len(staff) == 0:
        title = "There is currently no staff member available."
    elif len(staff) == 1:
        title = "One Staff Member is Available"
    else:
        title = f"{len(staff)} Staff Members Available"
    desc_list = [ctx.get_guild().get_member(s["user_id"]).mention for s in staff]
    if not desc_list:
        await ctx.respond(embed=client.fast_embed(title))
    else:
        await ctx.respond(embed=client.fast_embed(
            title,
            f"DM him/her to get help/information.\n\n{', '.join(desc_list)}"))


@component.with_slash_command
@tanjun.with_check(is_admin)
@tanjun.with_member_slash_option("member", "Add this member to the Staff group")
@tanjun.with_str_slash_option(
    "permissions",
    "What permissions should the user has",
    choices=[key for key in PERMISSIONS], default="register")
@tanjun.as_slash_command("add_staff", "Manage Staff")
async def add_staff(
        ctx: tanjun.abc.SlashContext,
        member: hikari.Member,
        permissions: str,
        client: ClanWarsClient = tanjun.injected(type=ClanWarsClient),
        bot: ClanWarsBot = tanjun.injected(type=ClanWarsBot)):
    pool: asyncpg.pool.Pool = client.db
    exe = f"INSERT INTO staff (user_id, {permissions}, joined) VALUES ($1, True, NOW());"
    await pool.execute(exe, member.id)
    await ctx.respond(client.fast_embed(description=f"{member.mention} Is now a staff member\n"
                                                    f"(Permissions: {permissions})"))


@component.with_slash_command
@tanjun.with_check(is_admin)
@tanjun.with_member_slash_option("member", "Set the Staff member available", default=None)
@tanjun.as_slash_command("available", "Set your/another staff members availability")
async def available(
        ctx: tanjun.abc.SlashContext,
        member: Optional[hikari.Member],
        client: ClanWarsClient = tanjun.injected(type=ClanWarsClient),
        bot: ClanWarsBot = tanjun.injected(type=ClanWarsBot)):
    pool: asyncpg.pool.Pool = client.db
    if not member:
        member = ctx.author
    x = await pool.fetchrow(f"UPDATE staff SET available=not available WHERE user_id = $1 "
                            f"RETURNING available", member.id)
    if x is None:
        await ctx.respond(embed=client.fast_embed(description=f"{member.mention} is not a staff member!"))
        return
    if x["available"] is True:
        await ctx.respond(embed=client.fast_embed(description=f"You are now available!", color=hikari.Color.from_rgb(0, 100, 0)))
    else:
        await ctx.respond(embed=client.fast_embed(description=f"You are not available anymore!", color=hikari.Color.from_rgb(100, 0, 0)))


@component.with_slash_command
@tanjun.with_check(is_admin)
@tanjun.with_member_slash_option("member", "Update this members Permissions")
@tanjun.with_str_slash_option(
    "single_permissions",
    "What permissions the staff member should get added/removed",
    choices=[key for key in PERMISSIONS],
    default=None
)
@tanjun.with_str_slash_option(
    "multiple_permissions",
    "Type in multiple Permissions the Staff member should get added_removed",
    default=None
)
@tanjun.as_slash_command("update_permissions", "Update Permissions of a staff member")
async def update_permissions(
        ctx: tanjun.abc.SlashContext,
        member: hikari.Member,
        single_permissions: Optional[str],
        multiple_permissions: Optional[str],
        client: ClanWarsClient = tanjun.injected(type=ClanWarsClient),
        bot: ClanWarsBot = tanjun.injected(type=ClanWarsBot)
):
    pool: asyncpg.pool.Pool = client.db
    if single_permissions:
        permissions = [single_permissions]
    elif multiple_permissions:
        permissions = [perm.strip() for perm in multiple_permissions.split(",")]
    elif single_permissions and multiple_permissions:
        permissions = [perm.strip() for perm in multiple_permissions.split(",")].append(single_permissions)
    else:
        await ctx.respond(embed=client.fast_embed(description="I need a permission to update a staff member"))
        return
    not_perm = []
    for perm in permissions:
        if perm not in [key for key in PERMISSIONS]:
            not_perm.append(perm)
            del permissions[permissions.index(perm)]
    db_staff = await pool.fetchrow("SELECT * FROM staff WHERE user_id=$1", member.id)
    if not db_staff:
        await ctx.respond(embed=client.fast_embed(description="The member is not a staff member"))
        return
    print([i for i in db_staff])
 

@component.with_slash_command
@tanjun.with_check(is_admin)
@tanjun.with_member_slash_option("member", "Remove this member to the Staff group")
@tanjun.as_slash_command("remove_staff", "Remove this Staff-Member from the Staff Team")
async def remove_staff(
        ctx: tanjun.abc.SlashContext,
        member: hikari.Member,
        client: ClanWarsClient = tanjun.injected(type=ClanWarsClient),
        bot: ClanWarsBot = tanjun.injected(type=ClanWarsBot)):
    pool: asyncpg.pool.Pool = client.db
    user = await pool.fetchrow("SELECT * FROM staff WHERE user_id = $1;", member.id)
    if user is None:
        await ctx.respond(client.fast_embed(description=f"{member.mention} is no staff-member."))
    else:
        await pool.execute("UPDATE staff SET active=False, left=NOW() WHERE user_id = $1;", member.id)


@tanjun.as_loader
def load_component(client: ClanWarsClient):
    client.add_component(component.copy())
