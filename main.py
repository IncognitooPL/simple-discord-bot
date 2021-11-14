import asyncio
import json
import discord
import random
from discord.ext import commands
from discord_components import Button, DiscordComponents, Select, SelectOption

bot = commands.Bot(command_prefix='!')  # Change bot prefix here
config = {}
credentials = {}


###################################
#          TICKET SYSTEM          #
###################################


@bot.command()
async def ticket(ctx):
    dialogues = config['ticket']['main_dialogues']
    dm_dialogues = config['ticket']['dm_confirmation_dialogues']
    ticket_config = config['ticket']['config']

    embed = discord.Embed(title=dialogues['ticket_header'],
                          description=dialogues['ticket_content'],
                          colour=int(ticket_config["ticket_colour"], 16))

    if str(ticket_config['show_author']).capitalize() == "True":
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

    if str(ticket_config['use_thumbnail']).capitalize() == "True":
        embed.set_thumbnail(url=dialogues['ticket_thumbnail_url'])

    if str(ticket_config['use_footer']).capitalize() == "True":
        if str(ticket_config['show_footer_img']).capitalize() == "True":
            if str(ticket_config['use_footer_custom_img']).capitalize() == "True":
                footer_img = dialogues['ticket_footer_custom_img_url']
            else:
                footer_img = ctx.guild.icon_url
            embed.set_footer(text=dialogues['ticket_footer'], icon_url=footer_img)
        else:
            embed.set_footer(text=dialogues['ticket_footer'])

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
            await message.delete()
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

    print("Created :" + str(channel))

    ###################################
    #       ANNOUNCEMENT SYSTEM       #
    ###################################


@bot.command()
async def announcement(ctx, *, message):
    if not checkAdminPermissions(ctx):
        await ctx.send(config['debug']['errors']['missing_permissions'])
        return

    anconfig = config['announcements']
    ping_everyone = ""

    if str(anconfig['config']['announcement_ping_everyone']).capitalize() == "True":
        ping_everyone = "@everyone"

    embed = discord.Embed(title=anconfig['announcement_title'],
                          description=message,
                          colour=int(anconfig["config"]['announcement_colour'], 16))

    if str(anconfig['config']['show_author']).capitalize() == "True":
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

    if str(anconfig['config']['use_thumbnail']).capitalize() == "True":
        embed.set_thumbnail(url=anconfig['announcement_thumbnail_url'])

    if str(anconfig['config']['use_footer']).capitalize() == "True":
        if str(anconfig['config']['show_footer_img']).capitalize() == "True":
            if str(anconfig['config']['use_footer_custom_img']).capitalize() == "True":
                footer_img = anconfig['announcement_footer_custom_img_url']
            else:
                footer_img = ctx.guild.icon_url
            embed.set_footer(text=anconfig['announcement_footer'], icon_url=footer_img)
        else:
            embed.set_footer(text=anconfig['announcement_footer'])

    await ctx.send(ping_everyone, embed=embed)

    ###################################
    #      ACTIVITY CHANGE SYSTEM     #
    ###################################


@bot.command()
async def changeActivity(ctx, *, args):
    if not checkAdminPermissions(ctx):
        await ctx.send(config['debug']['errors']['missing_permissions'])
        return

    ca_config = config['changeActivity']

    components = [
        Select(
            placeholder=ca_config['select_title'],
            options=[
                SelectOption(label=ca_config['activity_types']['playing'], value=0),
                # SelectOption(label=ca_config['activity_types']['streaming'], value=1),
                SelectOption(label=ca_config['activity_types']['listening'], value=2),
                SelectOption(label=ca_config['activity_types']['competing'], value=3),
                SelectOption(label=ca_config['activity_types']['watching'], value=4)
            ],
            custom_id="selected",
        )
    ]

    await ctx.send(ca_config['choose_activity_type'], components=components)

    interaction = await bot.wait_for(
        "select_option", check=lambda inter: inter.custom_id == "selected"
    )

    if int(interaction.values[0]) == 0:
        activity = discord.Game(name=args)
    elif int(interaction.values[0]) == 1:
        activity = discord.Streaming(name="contact me :DDD", url="kontakt@incognitoo.pl")
    elif int(interaction.values[0]) == 2:
        activity = discord.Activity(type=discord.ActivityType.listening, name=args)
    elif int(interaction.values[0]) == 3:
        activity = discord.Activity(type=discord.ActivityType.competing, name=args)
    elif int(interaction.values[0]) == 4:
        activity = discord.Activity(type=discord.ActivityType.watching, name=args)
    else:
        await ctx.send(ca_config['error'])
        return

    if bool(args):
        print(args)

    await bot.change_presence(activity=activity)
    await interaction.send(content=f"{interaction.values[0]} selected!")

    ###################################
    #         OTHER COMMANDS          #
    #         AND FUNCTIONS           #
    ###################################


'''
@bot.command() # TO DO
async def help(ctx, *, message):
    if checkAdminPermissions(ctx):
        await ctx.message.delete()
        await ctx.send(message)'''


@bot.command()
async def say(ctx, *, message):
    if checkAdminPermissions(ctx):
        await ctx.message.delete()
        await ctx.send(message)


def checkAdminPermissions(ctx):
    allowed = False

    for userRole in ctx.author.roles:
        for accessedRoles in config['debug']['debug_accessed_roles']:
            if int(accessedRoles) == userRole.id:
                allowed = True

    return allowed

    ###################################
    #           DEBUG TOOLS           #
    ###################################


@bot.command()
async def ping(ctx):
    if checkAdminPermissions(ctx):
        await ctx.send(config['debug']['ping'])
    else:
        await ctx.send(config['debug']['errors']['missing_permissions'])


@bot.command()
async def reload(ctx):
    if checkAdminPermissions(ctx):
        loadFiles()
        await ctx.send(config['debug']['reload'])
    else:
        await ctx.send(config['debug']['errors']['missing_permissions'])

'''
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(config['debug']['errors']['MissingRequiredArgument'])
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(config['debug']['errors']['CommandNotFound'])
    else:
        await ctx.send(config['debug']['errors']['unexpected_error'])'''

    ###################################
    #          SETUP STATEMENT        #
    ###################################


@bot.event
async def on_ready():  # Remember: don't 👏 do 👏 shit 👏 in 👏 on_ready.
    print(config['debug']['motd'])
    DiscordComponents(bot)


def loadFiles():
    global config
    global credentials
    config = json.load(open('config.json', encoding='utf-8'))['config']
    credentials = json.load(open('credentials.json'))


def setup():
    loadFiles()
    bot.run(credentials['token'])


setup()
