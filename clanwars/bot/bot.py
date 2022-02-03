import asyncio
import typing
from datetime import datetime

import hikari
from hikari import presences

from clanwars import CLAN_WARS_GUILD_ID, __version__
from clanwars.bot.client import ClanWarsClient
from clanwars.bot.utils import setup

_BotT = typing.TypeVar("_BotT", bound="ClanWarsBot")


class ClanWarsBot(hikari.GatewayBot):
    def __init__(self):
        self.__version__ = "0.0.1"
        self.db = asyncio.get_event_loop().run_until_complete(setup.setup_database_pool())
        CONFIG = setup.get_config()
        super().__init__(
            token=CONFIG["token"],
            intents=hikari.Intents.ALL
        )

    def create_client(self: _BotT):
        self.client = ClanWarsClient.from_gateway_bot(self, set_global_commands=CLAN_WARS_GUILD_ID)
        self.client.load_modules()

    def run(self, *args, **kwargs):
        self.create_client()
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)

        super().run(
            activity=presences.Activity(name=f"/help | BotVersion  {__version__}", type=presences.ActivityType.WATCHING),
            status=presences.Status.IDLE,
            idle_since=datetime.utcnow()
        )

    async def on_started(self, event):
        print("Bot Started!")