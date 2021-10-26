import                      asyncio
import                      json
import                      discord
from discord_components     import Button, ComponentsBot

bot = ComponentsBot("!")

dialogues = json.load(open('dialogues.json'))


@bot.command()
async def embed(ctx):
    embed = discord.Embed(title="Wyślij Zgłoszenie",
                          description="Bla bla wysyłanie zgłoszenia śmieszne lol xd beczooonia chcesz to wysłać byqu?",
                          color=0x3D85C6)

    components = [
        [
            Button(label='Potwierdź', style=3, custom_id='button_1'),
            Button(label='Odrzuć', style=4, custom_id='button_2')
        ]
    ]

    message = await ctx.send(embed=embed, components=components)

    while True:
        try:
            interaction = await bot.wait_for(
                'button_click',
                check=lambda inter: inter.message.id == message.id,
                timeout=60
            )
        except asyncio.TimeoutError:
            for row in components:
                row.disable_components()
            return await message.edit(content='Timed out!', components=components)

        if interaction.custom_id == 'button_1':
            await interaction.send('Hey! Whats up?')
        elif interaction.custom_id == 'button_2':
            await interaction.send('Wow! You clicked `Button 2`')


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


@bot.event
async def on_ready():
    print(dialogues['dialogues']['debug']['motd'])


bot.run('TOKEN HERE')
