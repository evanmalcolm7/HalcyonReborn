import discord
from discord.ext import commands
import functools

from config import TOKEN
from files import get_file, save_file
from botInterface import Payload, payload_manage

# needs to have access to everything that could possibly be pickled
from players import *
from regions import *
from vehicles import *

client = discord.Client()
bot = commands.Bot(command_prefix='~')


def region_string_to_int(region_string):
    '''Converts a string '(x, y)' to a tuple (x, y)'''
    splitforms = region_string.split(',')
    nospaces = [x.replace(' ', '') for x in splitforms]
    noparens = [x.replace('(', '') for x in nospaces]
    noparens2 = [x.replace(')', '') for x in noparens]
    asints = [int(x) for x in noparens2]
    return (asints[0], asints[1])


def entity_display_to_id(entity_display):
    '''Converts an entity's display name to its internal ID'''
    # * entity display will be in the form "Owners's Entity | "
    # * we need it to be in the form OWNERentity
    # first, we strip it into two words
    try:
        owner, entity = entity_display.split()
    except ValueError:  # unless it's already one word
        return entity_display
    # for owner, we remove the 's and uppercase it
    owner = owner[:-2].upper()
    # for entity, we just lowercase it
    entity = entity.lower()
    # then for the return we just combine the two
    return owner + entity


def error_helper(coro):
    @functools.wraps(coro)
    async def wrapper(*args, **kwargs):
        try:
            return await coro(*args, **kwargs)
        except KeyError as e:
            print(f'KeyError: {e}')
            ctx = args[0]
            return await ctx.send(f'```ERROR: No match found for the key {e}.```')
        except ValueError as e:
            print(f'ValueError: {e}')
            ctx = args[0]
            return await ctx.send('```ERROR: ValueError. Check your spaces and quotes!```')
        except AttributeError as e:
            print(f'AttributeError: {e}')
            ctx = args[0]
            return await ctx.send('```ERROR: Target does not possess that ability.')
    return wrapper


@bot.command()
async def register_player(ctx, player_name):
    uid = ctx.message.author.id
    # make sure this is a unique player
    Players = get_file('Players.pickle')
    if uid in list(Players.keys()):
        await ctx.send('Error: you\'re already registered!')
        return
    # make sure this is a unique username
    if player_name in [p.name for p in Players.values()]:
        await ctx.send('Error: a player already has this name!')
        return
    # if both of those are math, initialize a Player object
    Player(uid, player_name)
    await ctx.send(f'Player {player_name} created with UID {uid}')
    return


@bot.command()
@error_helper
async def scan_region(ctx, target_xy):
    Regions = get_file('Regions.pickle')
    # translate coords to actual region object
    target_region = Regions[region_string_to_int(target_xy)]
    result = target_region.scan()
    output = payload_manage(result)
    await ctx.send(output)


@bot.command()
@error_helper
async def inspect(ctx, entity_display_string, target_xy):
    # first, we get the region python_object we want
    Regions = get_file('Regions.pickle')
    target_region = Regions[region_string_to_int(target_xy)]
    # then we get the target entity's internal ID
    target_entity_id = entity_display_to_id(entity_display_string)
    # then we get the actual object we want
    inspect_target = target_region.content[target_entity_id]
    # inspect it and send the result to payload manager
    output = payload_manage(inspect_target.A_inspect())
    await ctx.send(output)

@bot.command()
@error_helper
async def use_ability(ctx, ability, *args)


bot.run(TOKEN)
