import tanjun

from clanwars.bot.client import ClanWarsClient

component = tanjun.Component()


@tanjun.as_loader
def load_component(client: ClanWarsClient):
    client.add_component(component.copy())