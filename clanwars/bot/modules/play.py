import asyncio
from typing import List

import asyncpg
import tanjun
import hikari
from hikari import PermissionOverwrite, PermissionOverwriteType, Permissions, ButtonStyle

from clanwars import CLAN_WARS_GUILD_ID
from clanwars.bot.bot import ClanWarsBot
from clanwars.bot.client import ClanWarsClient
from clanwars.bot.utils.play import check_clan
from clanwars.bot.utils.checks import can_score, can_score_listener


component = tanjun.Component()

CHANNELS = {
    "3v3": {
        "team1": 894316552084672572,
        "team2": 894316856326881324
    },
    "4v4": {
        "team1": 894322356242251806,
        "team2": 894322374256783420
    }
}


@component.with_listener(hikari.events.voice_events.VoiceStateUpdateEvent)
async def start(event: hikari.events.voice_events.VoiceStateUpdateEvent,
                cache: hikari.api.Cache = tanjun.injected(type=hikari.api.Cache)):
    channels = []
    guild = await event.app.rest.fetch_guild(event.state.guild_id)
    for mode in CHANNELS:
        for team in CHANNELS[mode]:
            channels.append(CHANNELS[mode][team])
    channel_1: hikari.channels.GuildVoiceChannel = guild.get_channel(CHANNELS["3v3"]["team1"])
    members_channel_1 = cache.get_voice_states_view_for_channel(guild, channel_1)
    if event.state.channel_id in channels or event.old_state.channel_id in channels:
        if event.state.channel_id is None:
            channel: hikari.channels.GuildChannel = guild.get_channel(event.old_state.channel_id)
        else:
            channel: hikari.channels.GuildChannel = guild.get_channel(event.state.channel_id)
        category: hikari.channels.GuildCategory = guild.get_channel(channel.parent_id)
        if category.name.startswith("3"):
            channel_1: hikari.channels.GuildVoiceChannel = guild.get_channel(CHANNELS["3v3"]["team1"])
            channel_2: hikari.channels.GuildVoiceChannel = guild.get_channel(CHANNELS["3v3"]["team2"])
        else:
            channel_1: hikari.channels.GuildVoiceChannel = guild.get_channel(CHANNELS["4v4"]["team1"])
            channel_2: hikari.channels.GuildVoiceChannel = guild.get_channel(CHANNELS["4v4"]["team2"])
        members_channel_1 = cache.get_voice_states_view_for_channel(guild, channel_1)
        members_channel_2 = cache.get_voice_states_view_for_channel(guild, channel_2)
        pool: asyncpg.pool.Pool = event.app.db
        clan_1_name, num_clan_1 = await check_clan(members_channel_1, pool)
        clan_2_name, num_clan_2 = await check_clan(members_channel_2, pool)
        if clan_1_name == clan_2_name:
            return
        if (num_clan_1 == 1) and (num_clan_2 == 1):
            member_1 = [guild.get_member(member_id) for member_id in members_channel_1]
            member_2 = [guild.get_member(member_id) for member_id in members_channel_2]
            await start_game(member_1, member_2, clan_1_name, clan_2_name, channel_1, channel_2, pool, guild, event)
        else:
            return

    else:
        return


async def start_game(
        members_clan_1: List[hikari.Member],
        members_clan_2: List[hikari.Member],
        clan_name_1: str,
        clan_name_2: str,
        channel_1: hikari.channels.GuildVoiceChannel,
        channel_2: hikari.channels.GuildVoiceChannel,
        pool: asyncpg.pool.Pool,
        guild: hikari.RESTGuild,
        event: hikari.events.voice_events.VoiceStateUpdateEvent):
    game_category: hikari.channels.GuildCategory = guild.get_channel(894314985394683944)

    channel_game_1 = await guild.create_voice_channel(
        name=clan_name_1,
        category=game_category,
        permission_overwrites=
        [
            PermissionOverwrite(
                type=PermissionOverwriteType.ROLE,
                deny=(
                    Permissions.VIEW_CHANNEL
                ),
                id=guild.id)] +
        [
            PermissionOverwrite(
                type=PermissionOverwriteType.MEMBER,
                allow=(
                        Permissions.VIEW_CHANNEL
                        | Permissions.SPEAK
                        | Permissions.STREAM
                ),
                id=member
            ) for member in members_clan_1 + members_clan_2
        ]
    )
    channel_game_2 = await guild.create_voice_channel(
        name=clan_name_2,
        category=game_category,
        permission_overwrites=
        [
            PermissionOverwrite(
                type=PermissionOverwriteType.ROLE,
                deny=(
                    Permissions.VIEW_CHANNEL
                ),
                id=guild.id)] +
        [
            PermissionOverwrite(
                type=PermissionOverwriteType.MEMBER,
                allow=(
                        Permissions.VIEW_CHANNEL
                        | Permissions.SPEAK
                        | Permissions.STREAM
                ),
                id=member
            ) for member in members_clan_1 + members_clan_2
        ]
    )
    channel_game = await guild.create_text_channel(
        name=f"{clan_name_1} vs {clan_name_2}",
        category=game_category,
        permission_overwrites=
        [
            PermissionOverwrite(
                type=PermissionOverwriteType.ROLE,
                deny=(
                    Permissions.VIEW_CHANNEL
                ),
                id=guild.id)] +
        [
            PermissionOverwrite(
                type=PermissionOverwriteType.MEMBER,
                allow=(
                        Permissions.VIEW_CHANNEL
                        | Permissions.SEND_MESSAGES
                        | Permissions.READ_MESSAGE_HISTORY
                ),
                id=member
            ) for member in members_clan_1 + members_clan_2]
    )

    for member in members_clan_1:
        await member.edit(voice_channel=channel_game_1)

    for member in members_clan_2:
        await member.edit(voice_channel=channel_game_2)

    game_id = await pool.fetchval("INSERT INTO games (text_channel_id, voice_channel_1, voice_channel_2, clan_1, clan_2, clan_1_members, clan_2_members) "
                                  "VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING game_id",
                                  channel_game.id, channel_game_1.id, channel_game_2.id, clan_name_1, clan_name_2, members_clan_1, members_clan_2)

    row = event.app.rest.build_action_row()
    (
        row.add_button(ButtonStyle.SECONDARY, "c1___" + clan_name_1)
            .set_label(clan_name_1)
            .set_emoji("1️⃣")
            .add_to_container(),
        row.add_button(ButtonStyle.SECONDARY, "c2___" + clan_name_2)
            .set_label(clan_name_2)
            .set_emoji("2️⃣")
            .add_to_container()
    )

    embed = hikari.embeds.Embed(
        title=f"Game #{game_id}",
        description="The game started\n"
                    "Play the game\n"
                    "Submit the game using the buttons below",
        color=hikari.Color.from_rgb(33, 200, 11)
    )
    embed.add_field(f"Clan 1️⃣ ({clan_name_1})", "\n".join([member.mention for member in members_clan_1]), inline=True)
    embed.add_field(f"Clan 2️⃣ ({clan_name_2})", "\n".join([member.mention for member in members_clan_2]), inline=True)

    message = await channel_game.send(
        "".join([member.mention for member in members_clan_1 + members_clan_2]),
        embed=embed,
        components=[row, ])

    await pool.execute("UPDATE games SET message_id=$1 WHERE game_id=$2", message.id, game_id)


@component.with_listener(hikari.events.interaction_events.InteractionCreateEvent)
async def on_interaction_create_event(event: hikari.events.interaction_events.InteractionCreateEvent,
                                      client: ClanWarsClient = tanjun.injected(type=ClanWarsClient),
                                      bot: ClanWarsBot = tanjun.injected(type=ClanWarsBot)):
    interaction = event.interaction
    pool: asyncpg.pool.Pool = event.app.db
    if isinstance(interaction, hikari.ComponentInteraction) and interaction.custom_id.startswith("c1___"):
        channel = await interaction.fetch_channel()
        guild = await interaction.fetch_guild()
        game_db = await pool.fetchrow("SELECT * FROM games WHERE text_channel_id=$1", channel.id)
        await pool.execute("UPDATE games SET winner=$1, submitted=$2 WHERE game_id=$3", game_db["clan_1"], True, game_db["game_id"])
        message = await channel.fetch_message(game_db["message_id"])
        embed = message.embeds[0]
        embed.description = "Thank you for playing\n" \
                            f"{interaction.member.mention} needs to send a ss of the result of the game in the chat\n" \
                            f"Else we would not score the game"
        embed.edit_field(0, f"Winner ({game_db['clan_1']}):",
                         "\n".join([guild.get_member(member).mention for member in game_db["clan_1_members"]]))
        embed.edit_field(1, f"Loser ({game_db['clan_2']}):",
                         "\n".join([guild.get_member(member).mention for member in game_db["clan_2_members"]]))
        await message.delete()
        games_channel = guild.get_channel(904709746500706304)
        row = event.app.rest.build_action_row()
        (
            row.add_button(ButtonStyle.SECONDARY, "sg___" + str(game_db["game_id"]))
                .set_label("Submit")
                .set_emoji("✅")
                .add_to_container(),
        )

        channel_message = await channel.send(embed=embed)

        while True:
            try:
                pic_event: hikari.events.message_events.GuildMessageCreateEvent = await bot.wait_for(
                    hikari.events.message_events.GuildMessageCreateEvent,
                    timeout=60
                )
                message = pic_event.message
                if message.author.id == interaction.member.id:
                    if not message.attachments:
                        embed.description = "You didn't send a picture in the chat (Try again)"
                        await channel_message.edit(embed=embed)
                    else:
                        attachments = message.attachments
                        if not attachments[0].media_type.startswith("image"):
                            embed.description = "The attachment you sent was not a image (Try again)"
                            await channel_message.edit(embed=embed)
                        else:
                            image = await attachments[0].read()
                            await message.delete()
                            break
                else:
                    continue
            except asyncio.exceptions.TimeoutError:
                row = event.app.rest.build_action_row()
                (
                    row.add_button(ButtonStyle.SECONDARY, "c1___" + game_db["clan_1"])
                        .set_label(game_db["clan_1"])
                        .set_emoji("1️⃣")
                        .add_to_container(),
                    row.add_button(ButtonStyle.SECONDARY, "c2___" + game_db["clan_2"])
                        .set_label(game_db["clan_2"])
                        .set_emoji("2️⃣")
                        .add_to_container()
                )
                embed.description = "Try to submit the game again using the buttons below."
                await message.edit(embed=embed, components=[row, ])
                return
        embed.description = "Thank you for playing"
        await pool.execute("UPDATE games SET winner=$1, submitted=$2, proof=$3 WHERE game_id=$4", game_db["clan_2"], True, image, game_db["game_id"])
        await games_channel.send(embed=client.fast_embed(description=f"Game #{game_db['game_id']} got submitted."), components=[row, ])

        await channel_message.edit(embed=embed)
        await asyncio.sleep(30)
        await channel.delete()
        for channel in [game_db["voice_channel_1"], game_db["voice_channel_2"]]:
            await guild.get_channel(channel).delete()

    elif isinstance(interaction, hikari.ComponentInteraction) and interaction.custom_id.startswith("c2___"):
        channel = await interaction.fetch_channel()
        guild = await interaction.fetch_guild()
        game_db = await pool.fetchrow("SELECT * FROM games WHERE text_channel_id=$1", channel.id)
        message = await channel.fetch_message(game_db["message_id"])
        embed = message.embeds[0]
        embed.description = "Thank you for playing\n" \
                            f"{interaction.member.mention} needs to send a ss of the result of the game in the chat\n" \
                            f"Else we would not score the game"
        embed.edit_field(0, f"Winner ({game_db['clan_2']}):",
                         "\n".join([guild.get_member(member).mention for member in game_db["clan_2_members"]]))
        embed.edit_field(1, f"Loser ({game_db['clan_1']}):",
                         "\n".join([guild.get_member(member).mention for member in game_db["clan_1_members"]]))
        await message.delete()
        games_channel = guild.get_channel(904709746500706304)
        row = event.app.rest.build_action_row()
        (
            row.add_button(ButtonStyle.SECONDARY, "sg___" + str(game_db["game_id"]))
                .set_label("Submit")
                .set_emoji("✅")
                .add_to_container()
        )

        channel_message = await channel.send(embed=embed)

        while True:
            try:
                pic_event: hikari.events.message_events.GuildMessageCreateEvent = await bot.wait_for(
                    hikari.events.message_events.GuildMessageCreateEvent,
                    timeout=60
                )
                message = pic_event.message
                if message.author.id == interaction.member.id:
                    if message.attachments is None:
                        embed.description = "You didn't send a picture in the chat (Try again)"
                        await channel_message.edit(embed=embed)
                    else:
                        attachments = message.attachments
                        if not attachments[0].media_type.startswith("image"):
                            embed.description = "The attachment you sent was not a image (Try again)"
                            await channel_message.edit(embed=embed)
                        else:
                            image = await attachments[0].read()
                            await message.delete()
                            break
                else:
                    continue
            except asyncio.exceptions.TimeoutError:
                row = event.app.rest.build_action_row()
                (
                    row.add_button(ButtonStyle.SECONDARY, "c1___" + game_db["clan_1"])
                        .set_label(game_db["clan_1"])
                        .set_emoji("1️⃣")
                        .add_to_container(),
                    row.add_button(ButtonStyle.SECONDARY, "c2___" + game_db["clan_2"])
                        .set_label(game_db["clan_2"])
                        .set_emoji("2️⃣")
                        .add_to_container()
                )
                embed.description = "Try to submit the game again using the buttons below."
                await channel_message.edit(embed=embed, components=[row, ])
                return
        embed.description = "Thank you for playing"
        await pool.execute("UPDATE games SET winner=$1, submitted=$2, proof=$3 WHERE game_id=$4", game_db["clan_2"], True, image, game_db["game_id"])
        await games_channel.send(embed=client.fast_embed(description=f"Game #{game_db['game_id']} got submitted."), components=[row, ])
        await channel_message.edit(embed=embed)
        await asyncio.sleep(30)
        await channel.delete()
        for channel in [game_db["voice_channel_1"], game_db["voice_channel_2"]]:
            await guild.get_channel(channel).delete()

    elif isinstance(interaction, hikari.ComponentInteraction) and interaction.custom_id.startswith("sg___"):
        check = await can_score_listener(pool, interaction.member)
        if isinstance(check, str):
            msg = await interaction.get_channel().send(client.fast_embed(description=check))
            await asyncio.sleep(10)
            await msg.delete()
            return
        await interaction.message.delete()
        channel = await interaction.fetch_channel()
        game_id = int(interaction.custom_id[5:])
        game_db = await pool.fetchrow("SELECT * FROM games WHERE game_id=$1", game_id)
        embed = hikari.embeds.Embed(
            title=f"Game #{game_id}",
            description=f"Check if it is true that {game_db['winner']} won the game"
        )
        embed.set_thumbnail(game_db["proof"])
        row = event.app.rest.build_action_row()
        (
            row.add_button(ButtonStyle.SECONDARY, "True")
               .set_label(game_db["winner"] + " Won")
               .set_emoji("✅")
               .add_to_container(),
            row.add_button(ButtonStyle.SECONDARY, "False")
               .set_label([game_db["clan_1"] if game_db["winner"] == game_db["clan_2"] else game_db["clan_2"]][0] + " Won")
               .set_emoji("❌")
               .add_to_container()
        )

        msg = await channel.send(embed=embed, components=[row, ])
        while True:
            try:
                check_event: hikari.events.interaction_events.InteractionCreateEvent = await bot.wait_for(
                    hikari.events.interaction_events.InteractionCreateEvent,
                    timeout=60
                )

                if (msg == check_event.interaction.message) and (check_event.interaction.member.id == interaction.member.id):
                    if bool(check_event.interaction.custom_id) is True:
                        pass
                    elif bool(check_event.interaction.custom_id) is False:
                        await pool.execute("UPDATE games SET winner=$1 WHERE game_id=$3",
                                           [game_db["clan_1"] if game_db["winner"] == game_db["clan_2"] else game_db["clan_2"]][0],
                                           game_db["game_id"])
                    break

                else:
                    continue
            except asyncio.exceptions.TimeoutError:
                embed.description = "You took too long to score the game"
                await msg.edit(embed=embed)
                await asyncio.sleep(5)
                embed.description = f"Check if it is true that {game_db['winner']} won the game"
                await msg.edit(embed=embed, components=[row, ])
                return
        row = event.app.rest.build_action_row()
        (
            row.add_button(ButtonStyle.SECONDARY, "sc___" + str(game_db["game_id"]))
               .set_label("Score the game Finally")
               .set_emoji("✅")
               .add_to_container()
        )
        embed.title = f"✅ Game #{game_db['game_id']}"
        embed.description = "If you press `Score the game Finally` the game gets scored."
        await msg.edit(embed=embed, components=[row, ])
        return

    elif isinstance(interaction, hikari.ComponentInteraction) and interaction.custom_id.startswith("sc___"):
        check = await can_score_listener(pool, interaction.member)
        if isinstance(check, str):
            msg = await interaction.get_channel().send(client.fast_embed(description=check))
            await asyncio.sleep(10)
            await msg.delete()
            return
        db = await pool.fetchrow("UPDATE games SET scored=$1 WHERE game_id=$2 RETURNING *", True, int(interaction.custom_id[5:]))
        await interaction.message.delete()
        games_channel = interaction.get_guild().get_channel(904787566228815872)
        await games_channel.send(client.fast_embed(
            title=f"Game #{interaction.custom_id[5:]} Scored",
            description=f"__{db['winner']}__ won the game **{db['clan_1']} vs {db['clan_2']}** (Scored by {interaction.member.mention})"))
        return


@tanjun.as_loader
def load_component(client: ClanWarsClient):
    client.add_component(component.copy())
