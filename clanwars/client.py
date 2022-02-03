import datetime

import hikari
import tanjun
import yuyo
from hikari import traits as hikari_traits

from clanwars.utils import get_config
from clanwars.database.model import Database


def build_gateway_bot() -> tuple[hikari.impl.GatewayBot, tanjun.Client]:
    bot = hikari.GatewayBot(
        get_config()["token"],
        intents=hikari.Intents.ALL,
    )
    return bot, build_from_gateway_bot(bot)


def build_from_gateway_bot(
        bot: hikari_traits.GatewayBotAware) -> tanjun.Client:
    component_client = yuyo.ComponentClient.from_gateway_bot(bot, event_managed=False)
    reaction_client = yuyo.ReactionClient.from_gateway_bot(bot, event_managed=False)
    db = Database()
    client = (tanjun.Client.from_gateway_bot(
        bot, declare_global_commands=894305669396697089,
        mention_prefix=True
    )
            .add_client_callback(tanjun.ClientCallbackNames.STARTING, component_client.open)
            .add_client_callback(tanjun.ClientCallbackNames.CLOSING, component_client.close)
            .add_client_callback(tanjun.ClientCallbackNames.STARTING, reaction_client.open)
            .add_client_callback(tanjun.ClientCallbackNames.CLOSING, reaction_client.close)
            .add_client_callback(tanjun.ClientCallbackNames.STARTING, db.create_database_pool)
            .set_type_dependency(yuyo.ReactionClient, reaction_client)
            .set_type_dependency(yuyo.ComponentClient, component_client)
            .set_type_dependency(Database, db)
            .load_modules("clanwars.modules"))
    (
        tanjun.InMemoryCooldownManager()
        .set_bucket("change_tag", tanjun.BucketResource.USER, 1, 20)
        .set_bucket("enable_disable_clan", tanjun.BucketResource.USER, 1, datetime.timedelta(hours=24))
        .add_to_client(client)
    )
    return client


def run_gateway_bot() -> None:
    bot, client = build_gateway_bot()
    bot.run()
