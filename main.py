import discord #import discord.py framework
import config #import config file

class MyClient(discord.Client):
    # Message on start
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    # When there is a change in the Voice Channels
    async def on_voice_state_update(self, member, before, after):
        # When a user joins the creation VC, create and move the user
        if after.channel and after.channel.id == config.CREATE_CHANNEL:
            guild = member.guild
            new_channel = await guild.create_voice_channel(f'{member.name} VC', category=after.channel.category)
            await member.move_to(new_channel)
            await new_channel.set_permissions(member, manage_channels=True)

        # If a VC is empty, delete it
        if len(before.channel.members) == 0 and before.channel.id != config.CREATE_CHANNEL:
            await before.channel.delete()

# Needed intends
intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.voice_states = True

# Start the Bot
client = MyClient(intents=intents)
client.run(config.TOKEN)
