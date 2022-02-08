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

import hikari
import tanjun
from hikari import traits as hikari_traits

from clanwars.utils import get_config, Database, Channels, User

INTENTS = hikari.Intents.GUILDS | hikari.Intents.ALL_MESSAGES | hikari.Intents.GUILD_MEMBERS


def build_gateway_bot() -> tuple[hikari.impl.GatewayBot, tanjun.Client]:
    bot = hikari.GatewayBot(
        get_config()["token"],
        intents=INTENTS,
    )
    return bot, build_from_gateway_bot(bot)


def build_from_gateway_bot(
        bot: hikari_traits.GatewayBotAware) -> tanjun.Client:
    db = Database()
    channel = Channels()
    users = User()
    client = (tanjun.Client.from_gateway_bot(
        bot, declare_global_commands=894305669396697089,
        # bot, declare_global_commands=True,
        mention_prefix=False)
              .set_type_dependency(Database, db)
              .set_type_dependency(Channels, channel)
              .set_type_dependency(User, users)
              .add_client_callback(tanjun.ClientCallbackNames.STARTING, db.create_database_pool)
              .load_modules("clanwars.modules"))
    return client


def run_gateway_bot() -> None:
    bot, client = build_gateway_bot()
    bot.run()
