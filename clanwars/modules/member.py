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
import asyncpg
import tanjun

from clanwars.utils import Database, respond


@tanjun.with_guild_check()
@tanjun.with_str_slash_option("ign", "Set your Ingame-Name")
@tanjun.as_slash_command("register", "Register yourself")
async def register_command(
        ctx: tanjun.SlashContext,
        ign: str,
        db: Database = tanjun.inject(type=Database)):
    insert = await db.insert_into("member", member_id=ctx.author.id, ign=ign)
    if insert is True:
        await respond(ctx, "Your clan got created", "approved")
    elif insert == "member_id":
        await respond(ctx, "You are already registered", "error")
    elif insert == "ign":
        await respond(ctx, "The Ingame-Name is already registered", "error")
    elif isinstance(insert, Exception):
        await respond(
            ctx,
            "An unexpected error occurred",
            "unexpected_error",
            f"**Who:**{ctx.author.mention}\n**Command:**/register `ign:{ign}`\n**Channel:**{ctx.get_channel().mention}\n{str(insert)}")


member_loader = tanjun.Component(name="member", strict=True).load_from_scope().make_loader()