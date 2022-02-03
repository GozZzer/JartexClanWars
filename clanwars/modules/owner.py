#  MIT License
#
#  Copyright (c) [2022] [GozZzer]
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
#  FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import hikari
import tanjun


@tanjun.with_owner_check
@tanjun.with_str_slash_option("command", "Type in the name of the command you want to delete")
@tanjun.as_slash_command("delete_command", "Deletes a Command")
async def delete_command(
        ctx: tanjun.abc.Context,
        command: str):
    commands = ctx.client.iter_slash_commands()
    try:
        await ctx.rest.delete_application_command(await ctx.client.rest.fetch_application(), [com.tracked_command for com in commands if com.name == command][0])
        await ctx.respond(f"{command} got deleted")
    except hikari.errors.NotFoundError:
        await ctx.respond(f"{command} does not exist")


owner_loader = tanjun.Component(name="owner", strict=True).load_from_scope().make_loader()