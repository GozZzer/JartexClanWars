import asyncio
import datetime

import hikari
import tanjun
from hikari import ButtonStyle

from clanwars.bot.bot import ClanWarsBot
from clanwars.bot.client import ClanWarsClient

component = tanjun.Component()

MODULES = {
    "clan": {
        "register_clan": {
            "description": "If you own a Clan on JartexNetwork and you want to play ClanWars, "
                           "register your clan using this command",
            "args": {
                "must": {
                    "clanname": {
                        "desc": "Insert the Guild Name which you want to register.",
                        "type": str
                    },
                    "membercount": {
                        "desc": "How many Members are in your Clan? (Include yourself)",
                        "type": int
                    }
                },
                "optional": {

                }
            },
            "checks": {
                "guild_check": "You are only allowed to use this Command in a guild"
            }
        },
        "delete_clan": {
            "description": "It deletes your Clan. You can reactivate your clan",
            "args": {
                "must": {
                    "clanname": {
                        "desc": "Insert the Guild Name which you want to register.",
                        "type": str
                    },
                    "membercount": {
                        "desc": "How many Members are in your Clan? (Include yourself)",
                        "type": int
                    }
                },
                "optional": {

                }
            },
            "checks": {
                "guild_check": "You are only allowed to use this Command in a guild"
            }

        },
        "reactivate": {

        },
        "add_member": {

        },
        "remove_member": {

        }

    },
    "member": {
        "register": {

        },
        "user_info": {

        },
        "add_alt": {

        }
    }
}


@component.add_slash_command
@tanjun.with_str_slash_option("module",
                              "Select if you want to get info about a specified module",
                              choices=["all", "clan", "member"], default="all")
@tanjun.as_slash_command("help", "Shows information about the bot")
async def help_command(
        ctx: tanjun.abc.SlashContext,
        module: str,
        client: ClanWarsClient = tanjun.injected(type=ClanWarsClient),
        bot: ClanWarsBot = tanjun.injected(type=ClanWarsBot)):
    embed = hikari.embeds.Embed(
        title="Help-Command",
        description="All infos you need to know about the bot.\n"
                    "If you still need help ask staff members or ask "
                    f"{ctx.get_guild().get_member(495874570104864788).mention}\n"
                    f"For more information about a module interact with the buttons",
        color=hikari.Color.from_rgb(66, 120, 33),
        timestamp=datetime.datetime.now(tz=datetime.timezone.utc)
    )
    row = ctx.rest.build_action_row()
    if module == "all" or module == "clan":
        embed.add_field(
            "Clan-Commands",
            "`register_clan`\n"
            "`delete_clan`\n"
            "`reactivate`\n"
            "`add_member`\n"
            "`remove_member\n`",
            inline=True
        )
        (
            row.add_button(ButtonStyle.SECONDARY, "h___" + "clan")
                .set_label("Clan")
                .add_to_container(),
        )
    if module == "all" or module == "member":
        embed.add_field(
            "Member-Commands",
            "`register`\n"
            "`user_info`\n"
            "`add_alt`\n",
            inline=True
        )
        (
            row.add_button(ButtonStyle.SECONDARY, "h___" + "member")
                .set_label("Member")
                .add_to_container(),
        )

    await ctx.respond(embed, components=[row, ])

    while True:
        try:
            event: hikari.events.interaction_events.InteractionCreateEvent = await bot.wait_for(
                hikari.events.interaction_events.InteractionCreateEvent,
                timeout=60
            )
            interaction = event.interaction
            if isinstance(interaction, hikari.ComponentInteraction) and interaction.custom_id == "h___clan":
                await interaction.message.delete()
                await interaction.create_initial_response(5)
            elif isinstance(interaction, hikari.ComponentInteraction) and interaction.custom_id == "h___member":
                await interaction.message.delete()
                await interaction.create_initial_response(5)

        except asyncio.exceptions.TimeoutError:
            try:
                await ctx.delete_last_response()
            except hikari.errors.NotFoundError:
                pass
            break


@tanjun.as_loader
def load_component(client: ClanWarsClient):
    client.add_component(component.copy())
