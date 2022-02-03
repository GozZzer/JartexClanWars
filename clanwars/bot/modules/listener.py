import asyncpg

import tanjun
import hikari
from hikari import ButtonStyle, events, CommandInteraction, ComponentInteraction

from clanwars.bot.client import ClanWarsClient

component = tanjun.Component()


@component.with_listener(events.interaction_events.InteractionCreateEvent)
async def on_interaction_create_event(event: hikari.events.interaction_events.InteractionCreateEvent):
    interaction = event.interaction
    if isinstance(interaction, CommandInteraction):
        pass
    elif isinstance(interaction, ComponentInteraction):
        pass


@tanjun.as_loader
def load_component(client: ClanWarsClient):
    client.add_component(component.copy())
