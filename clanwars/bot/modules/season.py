import datetime
import asyncpg
import hikari
import tanjun
import random

from clanwars.bot.client import ClanWarsClient
from clanwars.bot.utils.setup import setup_postgres_database_pool

UPDATE_CHANNEL = 894315193071443979
VOTE_MAPS_CHANNEL = 916416025375944726
VOTE_ITEMS_CHANNEL = 916416054094352434
NEW_SEASON_ROLE = 916416097111134219

MAPS = ["Oasis", "Crash", "Kongoisland", "Pirates", "Bowser", "Sonic", "Mariocircuit", "Joshi", "Summer", "Bastion", "Portal"]

NUMBERS = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

ITEMS = {
    "bbob": [
        "Punch Bow",
        "Diamond Armor",
        "Obsidian",
        "Knockback Stick",
        "TNT",
        "Iron Golem",
        "Enderpearl",
        "Water Bucket",
        "Pots",
        "Clay",
        "Emeralds"
    ],
    "Talents": ["OFF", "ON"],
    "Iron-Generator Speed": ["½x", "Normal", "2x", "3x"],
    "Gold-Generator Speed": ["½x", "Normal", "2x", "3x"],
    "Diamond-Generator Speed": ["½x", "Normal", "2x", "3x"],
    "Emerald-Generator Speed": ["½x", "Normal", "2x", "3x"],
}

DATA = ["map2", "map3", "map4", "map5", "map6", "Talents", "bbob",
        "Iron-Generator Speed", "Gold-Generator Speed", "Emerald-Generator Speed",
        "Diamond-Generator Speed"]

component = tanjun.Component()


@component.add_slash_command
@tanjun.as_slash_command("start_vote", "Generates a list of items for the current season.")
async def items_season(
        ctx: tanjun.abc.SlashContext,
        client: ClanWarsClient = tanjun.injected(type=ClanWarsClient)):
    pool: asyncpg.pool.Pool = client.db
    data = await pool.fetchrow("SELECT * FROM seasons WHERE season = (SELECT MAX(season) FROM seasons)")
    if data is None:
        current_season = 0
    else:
        current_season = data["season"]
        if data["voted"] is False:
            await ctx.respond(f"The vote is already started for season {current_season}")
            return
        elif data["voted"] is True and data["start_date"] is None:
            await ctx.respond(f"The vote is already done for season {current_season}")
            return
        elif data["voted"] is True and data["start_date"] is not None and data["end_date"] is None:
            await ctx.respond(f"The season {current_season} has already started")
            return
        elif data["voted"] is True and data["start_date"] is not None and data["end_date"] is not None:
            current_season += 1
            pass
    if current_season == 0:
        current_season = "beta"

    new_season_role = ctx.get_guild().get_role(NEW_SEASON_ROLE)

    # setup the vote for the maps
    map_chat = await client.rest.fetch_channel(VOTE_MAPS_CHANNEL)

    vote_maps = []
    maps = MAPS
    for i in range(5):
        map_1 = random.choice(maps)
        map_2 = random.choice(maps)
        while map_1 == map_2:
            map_2 = random.choice(maps)
        vote_maps.append([map_1, map_2])
        del maps[maps.index(map_1)]
        del maps[maps.index(map_2)]
    await map_chat.send(f"||{new_season_role.mention}||\n**Map vote for Season #{current_season}!**\n")
    current_season = 0 if current_season == "beta" else current_season
    await map_chat.send(f"**Map 1:** {maps[0]}\n")
    await pool.execute("INSERT INTO seasons (season, maps) VALUES ($1, $2)", current_season, [maps[0]])
    for i in range(0, 5):
        message = await map_chat.send(f"**Map {i + 2}:**\n>>> {vote_maps[i][0]}    \nvs \n{vote_maps[i][1]}\n")
        await message.add_reaction("1️⃣")
        await message.add_reaction("2️⃣")
        await pool.execute("INSERT INTO votes (vote_name, message_id, options, emojis) VALUES ($1, $2, $3, $4)",
                           f"map{i + 2}_season{current_season}",
                           message.id,
                           [vote_maps[i][0], vote_maps[i][1]],
                           ["1️⃣", "2️⃣"])

    # setup the vote for the items
    item_chat = await client.rest.fetch_channel(VOTE_ITEMS_CHANNEL)
    await item_chat.send(f"||{new_season_role.mention}||\n**Item vote for Season #{current_season}!**\n")
    for key in ITEMS:
        if key == "bbob":
            items = ""
            for item in ITEMS[key]:
                items = f"{items}\n{NUMBERS[ITEMS[key].index(item)]} {item}, "
            message = await item_chat.send(f"**Select the items you want to be enabled when your bed breaks\n"
                                           f"The other ones will be banned totally (for this season):**\n"
                                           f">>> {items[:-2]}")
            for emoji in NUMBERS:
                await message.add_reaction(emoji)
            await pool.execute("INSERT INTO votes (vote_name, message_id, options, emojis) VALUES ($1, $2, $3, $4)",
                               f"{key}_season{current_season}",
                               message.id,
                               ITEMS[key],
                               NUMBERS)
        else:
            options = "\n".join(ITEMS[key])
            message = await item_chat.send(f"**{key}:**\n"
                                           f">>> {options}")
            for i in range(0, len(ITEMS[key])):
                await message.add_reaction(NUMBERS[i])
            await pool.execute("INSERT INTO votes (vote_name, message_id, options, emojis) VALUES ($1, $2, $3, $4)",
                               f"{key}_season{current_season}",
                               message.id,
                               ITEMS[key],
                               [NUMBERS[num] for num in range(0, len(ITEMS[key]))])

    await ctx.respond("Done! The players are now allowed to vote for maps/items")


@component.add_slash_command
@tanjun.as_slash_command("stop_vote", "Stops the current vote.")
async def stop_vote(
        ctx: tanjun.abc.SlashContext,
        client: ClanWarsClient = tanjun.injected(type=ClanWarsClient)):
    pool: asyncpg.pool.Pool = client.db
    data = await pool.fetchrow("SELECT * FROM seasons WHERE season = (SELECT MAX(season) FROM seasons)")
    if data is None:
        current_season = 0
    else:
        current_season = data["season"]
        if data["voted"] is False:
            pass
        elif data["voted"] is True and data["start_date"] is None:
            await ctx.respond(f"The vote is already done for season {current_season}")
            return
        elif data["voted"] is True and data["start_date"] is not None and data["end_date"] is None:
            await ctx.respond(f"The season {current_season} has already started")
            return
        elif data["voted"] is True and data["start_date"] is not None and data["end_date"] is not None:
            current_season += 1
            pass

    map_chat = await client.rest.fetch_channel(VOTE_MAPS_CHANNEL)
    items_chat = await client.rest.fetch_channel(VOTE_ITEMS_CHANNEL)

    # Get the maps
    maps = []
    map_votes = []
    for i in range(2, 6 + 1):
        map_votes.append(await pool.fetchrow("SELECT * FROM votes WHERE vote_name = $1", f"map{i}_season{current_season}"))
    maps = {}

    for map_vote in map_votes:
        try:
            message = await map_chat.fetch_message(map_vote['message_id'])
            reactions = message.reactions

            if len(reactions) == len(map_vote['emojis']):
                for i in range(0, len(map_vote["emojis"])):
                    try:
                        maps[str(len(map_vote[f"option{i}"]))].append(map_vote["options"][i])
                    except KeyError:
                        maps[str(len(map_vote[f"option{i}"]))] = [map_vote["options"][i]]
            else:
                gozzer_dm = await client.rest.create_dm_channel(495874570104864788)
                await gozzer_dm.send(f"{ctx.author.mention} ({ctx.author}) tried to stop the map-vote but some reactions got deleted. (Len)")
                return

        except IndexError:
            gozzer_dm = await client.rest.create_dm_channel(495874570104864788)
            await gozzer_dm.send(f"{ctx.author.mention} ({ctx.author}) tried to stop the map-vote but some reactions got deleted. (Index)")
            return
        except hikari.errors.NotFoundError:
            gozzer_dm = await client.rest.create_dm_channel(495874570104864788)
            await gozzer_dm.send(f"{ctx.author.mention} ({ctx.author}) tried to stop the map-vote but a message got deleted.")
            return

    # Get the items
    items = {}
    item_votes = []
    for key in ITEMS:
        item_votes.append(await pool.fetchrow("SELECT * FROM votes WHERE vote_name = $1", f"{key}_season{current_season}"))
    for item_vote in item_votes:
        try:
            message = await items_chat.fetch_message(item_vote['message_id'])
            reactions = message.reactions

            if len(reactions) == len(item_vote['emojis']):
                for i in range(0, len(item_vote["emojis"])):
                    try:
                        items[str(len(item_vote[f"option{i}"]))].append(f"{item_votes.index(item_vote)}_" + item_vote["options"][i])
                    except KeyError:
                        items[str(len(item_vote[f"option{i}"]))] = [f"{item_votes.index(item_vote)}_" + item_vote["options"][i]]
            else:
                gozzer_dm = await client.rest.create_dm_channel(495874570104864788)
                await gozzer_dm.send(f"{ctx.author.mention} ({ctx.author}) tried to stop the map-vote but some reactions got deleted. (Len)")
                return

        except IndexError:
            gozzer_dm = await client.rest.create_dm_channel(495874570104864788)
            await gozzer_dm.send(f"{ctx.author.mention} ({ctx.author}) tried to stop the item-vote but some reactions got deleted. (Index)")
            return
        except hikari.errors.NotFoundError:
            gozzer_dm = await client.rest.create_dm_channel(495874570104864788)
            await gozzer_dm.send(f"{ctx.author.mention} ({ctx.author}) tried to stop the item-vote but a message got deleted.")
            return

    maps = {k: v for k, v in sorted(maps.items(), reverse=True)}
    items = {k: v for k, v in sorted(items.items(), reverse=True)}
    end_maps = []
    end_items = []
    end_igs = []
    end_ggs = []
    end_egs = []
    end_dgs = []
    talents = []
    highest = list(maps)[0]
    item_highest = list(items)[0]

    while len(end_maps) < 5:
        try:
            end_maps.append(random.choice(maps[str(highest)]))
            maps[str(highest)].remove(end_maps[-1])
        except IndexError:
            highest -= 1

    highest = item_highest
    while len(talents) == 0:
        talents = [tal[2:] for tal in items[str(highest)] if tal.startswith("1_")]
        if len(talents) == 0:
            highest -= 1
            continue
        elif len(talents) == 2:
            talent = random.choice(talents)
        else:
            talent = talents[0]
        if talent == "ON":
            talent = True
        else:
            talent = False

    highest = item_highest
    while len(end_items) < 6:
        try:
            end_items.append(random.choice([item for item in items[str(highest)] if item.startswith("0_")])[2:])
            items[str(highest)].remove(f"0_{end_items[-1]}")
        except IndexError:
            highest -= 1

    highest = item_highest
    while len(end_igs) == 0:
        igs = [ig[2:] for ig in items[str(highest)] if ig.startswith("2_")]
        if len(igs) == 0:
            highest -= 1
            continue
        elif len(igs) > 1:
            end_igs.append(random.choice(igs))
            items[str(highest)].remove(f"2_{end_igs[-1]}")
        else:
            end_igs.append(igs[0])
            items[str(highest)].remove(f"2_{end_igs[-1]}")

    highest = item_highest
    while len(end_ggs) == 0:
        ggs = [ig[2:] for ig in items[str(highest)] if ig.startswith("3_")]
        if len(ggs) == 0:
            highest -= 1
            continue
        elif len(ggs) > 1:
            end_ggs.append(random.choice(ggs))
            items[str(highest)].remove(f"3_{end_ggs[-1]}")
        else:
            end_ggs.append(ggs[0])
            items[str(highest)].remove(f"3_{end_ggs[-1]}")

    highest = item_highest
    while len(end_egs) == 0:
        egs = [ig[2:] for ig in items[str(highest)] if ig.startswith("4_")]
        if len(egs) == 0:
            highest -= 1
            continue
        elif len(egs) > 1:
            end_egs.append(random.choice(egs))
            items[str(highest)].remove(f"4_{end_egs[-1]}")
        else:
            end_egs.append(egs[0])
            items[str(highest)].remove(f"4_{end_egs[-1]}")

    highest = item_highest
    while len(end_dgs) == 0:
        dgs = [ig[2:] for ig in items[str(highest)] if ig.startswith("5_")]
        if len(dgs) == 0:
            highest -= 1
            continue
        elif len(dgs) > 1:
            end_dgs.append(random.choice(dgs))
            items[str(highest)].remove(f"5_{end_dgs[-1]}")
        else:
            end_dgs.append(dgs[0])
            items[str(highest)].remove(f"5_{end_dgs[-1]}")

    await pool.execute("UPDATE seasons SET "
                       "maps = maps || $1, "
                       "voted = $2,"
                       "items = $3,"
                       "talents = $4,"
                       "igs = $5,"
                       "ggs = $6,"
                       "egs = $7,"
                       "dgs = $8,"
                       "items_banned = $9 "
                       "WHERE season = $10",
                       end_maps,
                       True,
                       end_items,
                       talent,
                       end_igs[0],
                       end_ggs[0],
                       end_egs[0],
                       end_dgs[0],
                       [banned for banned in ITEMS["bbob"] if banned not in end_items],
                       current_season)
    for vote in DATA:
        print(await pool.execute("UPDATE votes SET finished = $1 WHERE vote_name = $2", True, vote + f"_season{current_season}"))
    await ctx.respond("Done! The vote is stopped now.")


@component.add_slash_command
@tanjun.as_slash_command("start_season", "Starts the new Season")
async def start_season(
        ctx: tanjun.abc.SlashContext,
        client: ClanWarsClient = tanjun.injected(type=ClanWarsClient)):
    pool: asyncpg.pool.Pool = client.db
    data = await pool.fetchrow("SELECT * FROM seasons WHERE season = (SELECT MAX(season) FROM seasons)")
    if data is None:
        current_season = 0
    else:
        current_season = data["season"]
        if data["voted"] is False:
            await ctx.respond(f"The voting is not done yet for season #{current_season}")
            return
        elif data["voted"] is True and data["start_date"] is not None and data["end_date"] is None:
            await ctx.respond(f"The season #{current_season} has already started")
            return
        elif data["voted"] is True and data["start_date"] is not None and data["end_date"] is not None:
            await ctx.respond(f"You need to start the vote first for season #{current_season}")
            return
        elif data["voted"] is True and data["start_date"] is None:
            pass
    await pool.execute(f"CREATE DATABASE season_{current_season}")
    season_pool = await setup_postgres_database_pool(f"season_{current_season}")
    await season_pool.execute(
        open("C:\\Users\\danie\\Desktop\\Programmieren\\Discord\\Current\\JartexClanWars\\clanwars\\bot\\utils\\database\\sqls\\new_season.sql", "r").read())
    await season_pool.close()

    update_chat = await client.rest.fetch_channel(UPDATE_CHANNEL)
    new_season_role = ctx.get_guild().get_role(NEW_SEASON_ROLE)
    if current_season == 0:
        current_season = "beta"
    await update_chat.send(f"||{new_season_role.mention}||\nSeason #{current_season} has started!")
    await pool.execute("UPDATE seasons SET start_date = $1 WHERE season = $2", datetime.datetime.utcnow(), current_season)
    await ctx.respond(f"The season #{current_season} has been started!")


@component.add_slash_command
@tanjun.as_slash_command("stop_season", "Ends the current season")
async def stop_season(
        ctx: tanjun.abc.SlashContext,
        client: ClanWarsClient = tanjun.injected(type=ClanWarsClient)):
    pool: asyncpg.pool.Pool = client.db
    data = await pool.fetchrow("SELECT * FROM seasons WHERE season = (SELECT MAX(season) FROM seasons)")
    if data is None:
        current_season = 0
    else:
        current_season = data["season"]
        if data["voted"] is False:
            await ctx.respond(f"The voting is not done yet for season #{current_season}")
            return
        elif data["voted"] is True and data["start_date"] is None:
            await ctx.respond(f"The season #{current_season} has not started yet")
            return
        elif data["voted"] is True and data["start_date"] is not None and data["end_date"] is not None:
            await ctx.respond(f"You need to start the vote first for the new season #{current_season + 1}")
            return
        elif data["voted"] is True and data["start_date"] is not None and data["end_date"] is None:
            pass
    await pool.execute("UPDATE seasons SET end_date = $1 WHERE season = $2", datetime.datetime.utcnow(), current_season)
    update_chat = await client.rest.fetch_channel(UPDATE_CHANNEL)
    new_season_role = ctx.get_guild().get_role(NEW_SEASON_ROLE)
    if current_season == 0:
        current_season = "beta"
    await update_chat.send(f"||{new_season_role.mention}||\nSeason #{current_season} has ended!")
    await pool.execute("UPDATE seasons SET end_date = $1 WHERE season = $2", datetime.datetime.utcnow(), current_season)
    await ctx.respond(f"The season #{current_season} has been ended!")


@component.with_listener(hikari.events.reaction_events.GuildReactionAddEvent)
async def reaction_add(event: hikari.events.reaction_events.GuildReactionAddEvent,
                       client: ClanWarsClient = tanjun.injected(type=ClanWarsClient)):
    pool: asyncpg.pool.Pool = client.db
    guild = await event.app.rest.fetch_guild(event.guild_id)
    channel = guild.get_channel(event.channel_id)
    message = await channel.fetch_message(event.message_id)
    user = await event.app.rest.fetch_user(event.user_id)
    data = await pool.fetchrow("SELECT * FROM votes WHERE message_id = $1", event.message_id)
    if data is None:
        return
    if event.member.id != 894899910137241640:
        if channel.id in [VOTE_MAPS_CHANNEL, VOTE_ITEMS_CHANNEL]:
            if event.emoji_name not in data["emojis"]:
                await message.remove_reaction(event.emoji_name, user=event.member)
                return
            voted = [data["emojis"][i] for i in range(0, len(data["emojis"])) if event.member.id in data[f"option{i}"]]
            if len(voted) + 1 <= round(len(data["emojis"]) / 2):
                index = data['emojis'].index(event.emoji_name)
                await pool.execute(f"UPDATE votes SET option{index} = option{index} || $1 WHERE message_id = $2", [int(event.member.id)], event.message_id)
            else:
                await message.remove_reaction(event.emoji_name, user=event.member)


@component.with_listener(hikari.events.reaction_events.GuildReactionDeleteEvent)
async def reaction_remove(event: hikari.events.reaction_events.GuildReactionDeleteEvent,
                          client: ClanWarsClient = tanjun.injected(type=ClanWarsClient)):
    pool: asyncpg.pool.Pool = client.db
    guild = await event.app.rest.fetch_guild(event.guild_id)
    channel = guild.get_channel(event.channel_id)
    data = await pool.fetchrow("SELECT * FROM votes WHERE message_id = $1", event.message_id)
    if data is None:
        return
    if event.user_id != 894899910137241640:
        if channel.id in [VOTE_MAPS_CHANNEL, VOTE_ITEMS_CHANNEL]:
            voted = [data["emojis"][i] for i in range(0, len(data["emojis"])) if event.user_id in data[f"option{i}"]]
            if event.emoji_name in voted:
                index = data['emojis'].index(event.emoji_name)
                await pool.execute(f"UPDATE votes SET option{index} = array_remove(option{index}, $1) WHERE message_id = $2", int(event.user_id), event.message_id)


@tanjun.as_loader
def load_component(client: ClanWarsClient):
    client.add_component(component.copy())
