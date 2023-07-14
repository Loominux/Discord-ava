import typing
import discord
import config
import json

data_file = "vc_owners.json"

try:
    with open(data_file, "r") as f:
        voice_channel_owners = json.load(f)
except FileNotFoundError:
    voice_channel_owners = {}

bot = discord.Bot()

# Bot starts
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

# User joins the creation VC Channel
@bot.event
async def on_voice_state_update(member, before, after):
    # When a user joins the creation VC, create and move the user
    if after.channel and after.channel.id == config.CREATE_CHANNEL:
        guild = member.guild
        new_channel = await guild.create_voice_channel(f'{member.name} VC', category=after.channel.category)
        await member.move_to(new_channel)
        await new_channel.set_permissions(member, manage_channels=True)

    # If a VC is empty, delete it
    if before.channel and len(before.channel.members) == 0 and before.channel.id != config.CREATE_CHANNEL:
        await before.channel.delete()

# Slash Command for Bot Ping
@bot.command(description="Sends the bot's latency.")
async def ping(ctx):
    await ctx.respond(f"Pong! Latency is {bot.latency} s", ephemeral=True)

# Slash Command for VC Channel creation
@bot.command(description="Create VC")
async def vc_create(ctx, name: typing.Optional[str] = None):
    guild = ctx.guild
    category = discord.utils.get(guild.categories, id=config.VC_CATEGORY)

    # Check if the user already owns a VC Channel, if they own one, error message and do nothing else
    if ctx.author.id in voice_channel_owners.values():
        await ctx.respond("You can only create one voice channel at a time.", ephemeral=True)
        return

    # If the name was Empty, set the name to the users name
    if name is None:
        name = ctx.author.name

    # Create new channel, give user permissions and respond to them
    new_channel = await category.create_voice_channel(name)
    await new_channel.set_permissions(ctx.author, manage_channels=True)
    await ctx.respond(f"Voice Channel {name} was successfully created", ephemeral=True)


    # Write User ID and VC Channel ID to the json
    voice_channel_owners[new_channel.id] = ctx.author.id
    with open(data_file, "w") as f:
        json.dump(voice_channel_owners, f)

# Remove user from Owner List, when VC Channel is deleted
@bot.event
async def on_guild_channel_delete(channel):
    # Enter when a VC Channel is deleted
    if isinstance(channel, discord.VoiceChannel):
        deleted_channel_id = channel.id

        # Check of the VC Channel belongs to a User
        for voice_channel_id, creator_id in list(voice_channel_owners.items()):
            if voice_channel_id == deleted_channel_id:
                # if that is the case remove entry from the json
                del voice_channel_owners[voice_channel_id]
                with open(data_file, "w") as f:
                    json.dump(voice_channel_owners, f)

bot.run(config.TOKEN)