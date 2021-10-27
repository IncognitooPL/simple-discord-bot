import asyncio
import json
import discord
from discord_components import Button, ComponentsBot

bot = ComponentsBot("!")

config = json.load(open('config.json', encoding='utf-8'))['dialogues']
credentials = json.load(open('credentials.json'))


@bot.command()
async def ticket(ctx):
    config = config['ticket']

    embed = discord.Embed(title=config['ticket_header'],
                          description=config['ticket_content'],
                          colour=int(config["ticket_colour"], 16))

    embed.set_footer(icon_url=ctx.guild.icon_url, text=config["ticket_footer"])

    components = [
        [
            Button(label=config['ticket_accept'], style=3, custom_id='button_1'),
            Button(label=config['ticket_discard'], style=4, custom_id='button_2')
        ]
    ]

    message = await ctx.send(embed=embed, components=components)

    while True:
        try:
            interaction = await bot.wait_for(
                'button_click',
                check=lambda inter: inter.message.id == message.id,
                timeout=config["ticket_timeout"]
            )

            print(interaction.guild.get_member(interaction.author.id))
        except asyncio.TimeoutError:
            for row in components:
                row.disable_components()
            return

        if interaction.custom_id == 'button_1':
            await interaction.send('Hey! Whats up?')
        elif interaction.custom_id == 'button_2':
            await interaction.send('Wow! You clicked `Button 2`')


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


def create_ticket(ctx):
    print("XD")


@bot.event
async def on_ready():
    print(config['debug']['motd'])


bot.run(credentials['token'])
