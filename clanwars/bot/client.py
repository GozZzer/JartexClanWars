import typing
import asyncio
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

import hikari
from tanjun import Client

from clanwars.bot.utils import setup

_ClientT = typing.TypeVar("_ClientT", bound="ClanWarsClient")


class ClanWarsClient(Client):
    __slots__ = Client.__slots__ + ("scheduler", "db")

    def __init__(self: _ClientT, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_prefix("L.")
        self.db = asyncio.get_event_loop().run_until_complete(setup.setup_database_pool())
        self.scheduler = AsyncIOScheduler()
        self.scheduler.configure(timezone=utc)

    def load_modules(self: _ClientT):
        return super().load_modules(*Path(__file__).parent.glob("modules/*.py"))

    def fast_embed(self: _ClientT, title: str = None, description: str = None, color: hikari.Color = None):
        return hikari.Embed(title=title, description=description, color=color)
