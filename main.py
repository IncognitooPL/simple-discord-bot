import asyncio
import json
import discord
import random
from discord import DMChannel, guild
from discord.ext import commands
from discord_components import Button, ComponentsBot, DiscordComponents

bot = commands.Bot(command_prefix='!')

DiscordComponents(bot)

config = json.load(open('config.json', encoding='utf-8'))['config']
credentials = json.load(open('credentials.json'))


@bot.command()
async def ticket(ctx):
    dialogues = config['ticket']['dialogues']
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
            return

        if interaction.custom_id == 'button_1' and interaction.author.id == ctx.author.id:
            await createTicketChannel(ctx, ctx.author)
            await message.delete()
            return

        elif interaction.custom_id == 'button_2' and interaction.author.id == ctx.author.id:
            await ctx.author.send("NOOOOO")
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
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True)
    }

    channel = await ctx.guild.create_text_channel(
        name=ticket_config['ticket_channel_name'] + str(ticketID),
        overwrites=overwrites)

    print(channel)


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


@bot.event
async def on_ready():
    print(config['debug']['motd'])


bot.run(credentials['token'])
