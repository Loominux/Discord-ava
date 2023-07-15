import typing
import discord
import config
import json

file_path = "vc_owners.json"
with open(file_path, "r") as json_file:
    voice_channel_owners = json.load(json_file)
json_file.close()

for item in voice_channel_owners:
    print(item["User_ID"])
    print(item["VC_Channel_ID"])

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

    # Check if the VC Channel is permanent
    permanent = False
    for item in voice_channel_owners:
        if before.channel.id == item["VC_Channel_ID"]:
            permanent = True

    # If a VC is empty, delete it
    if before.channel and len(before.channel.members) == 0 and before.channel.id != config.CREATE_CHANNEL and not permanent:

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

    # Check if the VC Channel is permanent
    for item in voice_channel_owners:
        if ctx.author.id == item["User_ID"]:
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
    Entry = {
        "User_ID": ctx.author.id,
        "VC_Channel_ID": new_channel.id
    }
    voice_channel_owners.append(Entry)

    print(Entry)

    with open(file_path, "w") as json_file:
        json.dump(voice_channel_owners, json_file, indent=4)

    json_file.close()

# Remove user from Owner List, when VC Channel is deleted
@bot.event
async def on_guild_channel_delete(channel):
    # Enter when a VC Channel is deleted
    if isinstance(channel, discord.VoiceChannel):
        deleted_channel_id = channel.id

        # Check if the VC Channel belongs to a User
        for item in voice_channel_owners:
            if deleted_channel_id == item["VC_Channel_ID"]:
                voice_channel_owners.remove(item)
                break  # Exit the loop once the item is found

        # Save the updated JSON data back to the file
        with open(file_path, "w") as json_file:
            json.dump(voice_channel_owners, json_file, indent=4)

bot.run(config.TOKEN)
