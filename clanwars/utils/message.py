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


async def respond(
        ctx: tanjun.SlashContext,
        message: str,
        message_type: str = None,
        error_info: str = None):
    """
    Types: error, unexpected_error, normal, approved, massive, info
    """
    embedd = hikari.Embed()
    if message_type == "error":
        embedd.description = message
        embedd.color = hikari.Color.from_rgb(255, 7, 58)
    elif message_type == "unexpected_error":
        embedd.description = message
        embedd.color = hikari.Color.from_rgb(139, 0, 0)
        await ctx.get_guild().get_channel(939276745046110208).send(hikari.Embed(
            description=error_info,
            color=hikari.Color.from_rgb(139, 0, 0)))
    elif message_type == "info":
        embedd.description = message
        embedd.color = hikari.Color.from_rgb(169, 169, 169)
    elif message_type == "normal":
        embedd.description = message
        embedd.color = hikari.Color.from_rgb(0, 255, 255)
    elif message_type == "approved":
        embedd.description = message
        embedd.color = hikari.Color.from_rgb(57, 255, 20)
    elif message_type == "massive":
        embedd.title = message
        embedd.color = hikari.Color.from_rgb(0, 255, 255)
    else:
        await ctx.respond(message)
        return
    await ctx.respond(embed=embedd)


async def send(
        channel,
        message: str,
        message_type: str = None,
        error_info: str = None,
        error_channel: hikari.TextableGuildChannel = None):
    """
    Types: error, unexpected_error, normal, approved, massive, info
    """
    embed = hikari.Embed()
    if message_type == "error":
        embed.description = message
        embed.color = hikari.Color.from_rgb(255, 7, 58)
    elif message_type == "unexpected_error":
        embed.description = message
        embed.color = hikari.Color.from_rgb(139, 0, 0)
        await error_channel.send(hikari.Embed(
            description=error_info,
            color=hikari.Color.from_rgb(139, 0, 0)))
    elif message_type == "info":
        embed.description = message
        embed.color = hikari.Color.from_rgb(169, 169, 169)
    elif message_type == "normal":
        embed.description = message
        embed.color = hikari.Color.from_rgb(0, 255, 255)
    elif message_type == "approved":
        embed.description = message
        embed.color = hikari.Color.from_rgb(57, 255, 20)
    elif message_type == "massive":
        embed.title = message
        embed.color = hikari.Color.from_rgb(0, 255, 255)
    else:
        await channel.send(message)
        return
    try:
        await channel.send(embed=embed)
        return True
    except hikari.errors.BadRequestError:
        return False


async def embed(
        ctx: tanjun.SlashContext,
        title=None,
        description=None,
        color: hikari.Color = None,
        **fields):
    embedd = hikari.Embed(title=title, description=description, color=color)
    for field in fields:
        embedd.add_field(field, fields[field], inline=False)
    await ctx.respond(embedd)
