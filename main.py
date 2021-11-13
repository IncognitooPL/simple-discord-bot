import asyncio
import json
import discord
import random
from discord.ext import commands
from discord_components import Button, DiscordComponents

bot         = commands.Bot(command_prefix='!')
config      = {}
credentials = {}


@bot.command()
async def ticket(ctx):
    dialogues = config['ticket']['main_dialogues']
    dm_dialogues = config['ticket']['dm_confirmation_dialogues']
    ticket_config = config['ticket']['config']

    embed = discord.Embed(title=dialogues['ticket_header'],
                          description=dialogues['ticket_content'],
                          colour=int(ticket_config["ticket_colour"], 16))

    embed.set_footer(icon_url=ctx.guild.icon_url, text=dialogues["ticket_footer"])

    components = [
        [
            Button(label=dialogues['ticket_accept'], style=3, custom_id='button_1'),
            Button(label=dialogues['ticket_discard'], style=4, custom_id='button_2')
        ]
    ]

    message = await ctx.send(embed=embed, components=components)

    while True:
        try:
            interaction = await bot.wait_for(
                'button_click',
                check=lambda inter: inter.message.id == message.id,
                timeout=ticket_config["ticket_timeout"]
            )

        except asyncio.TimeoutError:
            for row in components:
                row.disable_components()
            message.delete()
            return

        if interaction.custom_id == 'button_1' and interaction.author.id == ctx.author.id:
            if str(config['ticket']['send_dm_confirmation_on_creation']).capitalize() == "True":
                embed = discord.Embed(title=dm_dialogues['ticket_header'],
                                      description=dm_dialogues['ticket_content'],
                                      colour=int(ticket_config["ticket_colour"], 16))
                embed.set_footer(icon_url=ctx.guild.icon_url, text=dm_dialogues["ticket_footer"])
                await ctx.author.send(embed=embed)

            await createTicketChannel(ctx, ctx.author)
            await message.delete()
            return

        elif interaction.custom_id == 'button_2' and interaction.author.id == ctx.author.id:
            await message.delete()
            return


async def createTicketChannel(ctx, user):
    ticket_config = config['ticket']['config']
    ticketID = random.randint(111111111, 999999999)

    for channel in ctx.guild.channels:
        if str(channel.name) == str(ticket_config['ticket_channel_name'] + str(ticketID)):
            await createTicketChannel(ctx, user)
            return

    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True),
        ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
    }

    for accessed_roles in ticket_config['ticket_accessed_roles']:
        accessed_roles = discord.utils.get(user.guild.roles, id=int(accessed_roles))
        overwrites[accessed_roles] = discord.PermissionOverwrite(read_messages=True)

    category = discord.utils.get(user.guild.categories, id=int(ticket_config['ticket_category']))

    channel = await ctx.guild.create_text_channel(
        name=ticket_config['ticket_channel_name'] + str(ticketID),
        overwrites=overwrites,
        category=category)

    print("Created :"+str(channel))


@bot.command()
async def ping(ctx):
    if checkAdminPermissions(ctx):
        await ctx.send(config['debug']['ping'])
    else:
        await ctx.send(config['debug']['missing_permissions'])


@bot.command()
async def reload(ctx):
    if checkAdminPermissions(ctx):
        loadFiles()
        await ctx.send(config['debug']['reload'])
    else:
        await ctx.send(config['debug']['missing_permissions'])


@bot.command()
async def say(ctx, *, message):
    await ctx.message.delete()
    await ctx.send(message)

'''Only for me :DD'''
@bot.command()
async def clearAllTickets(ctx, category_id):
    category = discord.utils.get(ctx.guild.categories, id=int(category_id))
    for channel in category.channels:
        await channel.delete()


@bot.event
async def on_ready():
    print(config['debug']['motd'])
    DiscordComponents(bot)


def checkAdminPermissions(ctx):
    allowed = False

    for userRole in ctx.author.roles:
        for accessedRoles in config['debug']['debug_accessed_roles']:
            if int(accessedRoles) == userRole.id:
                allowed = True

    return allowed


def loadFiles():
    global config
    global credentials
    config = json.load(open('config.json', encoding='utf-8'))['config']
    credentials = json.load(open('credentials.json'))


def setup():
    loadFiles()
    bot.run(credentials['token'])


setup()

