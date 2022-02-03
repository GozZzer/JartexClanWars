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

import tanjun
import hikari

from clanwars.database import Database
from clanwars.discord.clanwar import check_start


clanwar_loader = tanjun.Component(name="clanwar", strict=True)


@clanwar_loader.with_listener(hikari.events.voice_events.VoiceStateUpdateEvent)
async def start(
        event: hikari.events.voice_events.VoiceStateUpdateEvent,
        cache: hikari.api.Cache = tanjun.injected(type=hikari.api.Cache),
        database: Database = tanjun.injected(type=Database)):
    clan_1, clan_2 = await check_start(event, cache, database.pool)


clanwar_loader.load_from_scope().make_loader()
