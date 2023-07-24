import typing
import discord
import config
import json

file_path = "vc_owners.json"
try:
    with open(file_path, "r") as json_file:
        try:
            voice_channel_owners = json.load(json_file)
        # Create Empty permanent VC list, when there is an JSON Decode error
        except json.JSONDecodeError:
            voice_channel_owners = []
except FileNotFoundError:
    # File not found, create a new file
    with open(file_path, "w") as json_file:
        json.dump([], json_file)
    voice_channel_owners = []

json_file.close()

print("Loading permanent Voice Channels:")

if voice_channel_owners:
    for item in voice_channel_owners:
        print("User_ID: " + str(item["User_ID"]))
        print("VC_Channel_ID: " + str(item["VC_Channel_ID"]) + "\n")

print("Loading completed")

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
        print("Temporary VC: " + member.name + " created VC with ID: " + str(new_channel.id))

    # Check if the VC Channel is permanent
    permanent = False
    if before.channel:
        for item in voice_channel_owners:
            if before.channel.id == item["VC_Channel_ID"]:
                permanent = True
                break

    # If a VC is empty, delete it
    if before.channel and len(before.channel.members) == 0 and before.channel.id != config.CREATE_CHANNEL and not permanent:
        await before.channel.delete()
        print("Temporary VC: deleted VC with ID: " + str(before.channel.id))

# Slash Command for Bot Ping
@bot.command(description="Sends the bot's latency.")
async def ping(ctx):
    await ctx.respond(f"Pong! Latency is {bot.latency} s", ephemeral=True)
    print(str(ctx.author.name) + "(" + str(ctx.author.id) + ") " + "requested the Bot latency, the current Latency is: " + str(bot.latency) + "s")

# Slash Command for VC Channel creation
@bot.command(description="Create VC")
async def vc_create(ctx, name: typing.Optional[str] = None):
    guild = ctx.guild
    category = discord.utils.get(guild.categories, id=config.VC_CATEGORY)

    # Check if the User already owns a VC
    for item in voice_channel_owners:
        if ctx.author.id == item["User_ID"]:
            await ctx.respond("You can only create one voice channel at a time.", ephemeral=True)
            print("Permanent VC: " + str(ctx.author.name) + "(" + str(ctx.author.id) + ") " + "tried to create more than one permanent Voice Channels")
            return

    if not any(role.id in config.PERMANENT_ROLES for role in ctx.author.roles):
        await ctx.respond("You don't have the rights to create a permanent Voice Channel", ephemeral=True)
        print("Permanent VC: " + str(ctx.author.name) + "(" + str(ctx.author.id) + ") " + "tried to create a permanent Voice Channel without the right role")
        return

    # If the name was Empty, set the name to the users name
    if name is None:
        name = "Permanent VC from " + ctx.author.name

    # Create new channel, give user permissions and respond to them
    new_channel = await category.create_voice_channel(name)
    await ctx.respond(f"Voice Channel {name} was successfully created", ephemeral=True)

    # Write User ID and VC Channel ID to the json
    Entry = {
        "User_ID": ctx.author.id,
        "VC_Channel_ID": new_channel.id
    }
    voice_channel_owners.append(Entry)

    print("Permanent VC: " + str(ctx.author.name) + "(" + str(ctx.author.id) + ") " + "created Voice Channel " + str(Entry["VC_Channel_ID"]))

    with open(file_path, "w") as json_file:
        json.dump(voice_channel_owners, json_file, indent=4)

    json_file.close()

# Slash command to change the user limit of a permanent VC
@bot.command(description="VC set User Limit")
async def vc_set_users(ctx, user_limit):
    # Search the user ID in the JSON with the owners
    if ctx.author.id:
        for item in voice_channel_owners:
            if ctx.author.id == item["User_ID"]:
                # When found, get the channel class and change the limit
                VCChannelID = discord.utils.get(bot.get_all_channels(), id=item["VC_Channel_ID"], type=discord.ChannelType.voice)
                if user_count == 0:
                    await VCChannelID.edit(user_limit=None)
                else:
                    await VCChannelID.edit(user_limit=user_count)
                await ctx.respond(f"Changed permanent VC User Count", ephemeral=True)
                break
    else:
        await ctx.respond(f"You don't own any permanent VCs", ephemeral=True)

# Slash command to change the name of a permanent VC
@bot.command(description="VC set Name")
async def vc_set_name(ctx, new_name):
    # Search the user ID in the JSON with the owners
    if ctx.author.id:
        for item in voice_channel_owners:
            if ctx.author.id == item["User_ID"]:
                # When found, get the channel class and change the name
                VCChannelID = discord.utils.get(bot.get_all_channels(), id=item["VC_Channel_ID"], type=discord.ChannelType.voice)
                await VCChannelID.edit(name=new_name)
                await ctx.respond(f"Changed permanent VC User Count", ephemeral=True)
                break
    else:
        await ctx.respond(f"You don't own any permanent VCs", ephemeral=True)

# Slash command to delete an permanent VC
@bot.command(description="Delete VC")
async def vc_delete(ctx):
    # Search the user ID in the JSON with the owners
    if ctx.author.id:
        for item in voice_channel_owners:
            if ctx.author.id == item["User_ID"]:
                # When found, delete the channel
                VCChannelID = discord.utils.get(bot.get_all_channels(), id=item["VC_Channel_ID"], type=discord.ChannelType.voice)
                await VCChannelID.delete()
                await ctx.respond(f"Permanent VC deleted", ephemeral=True)
                break

    else:
        await ctx.respond(f"You dont own an permanent VC", ephemeral=True)

# Remove user from Owner List, when VC Channel is deleted
@bot.event
async def on_guild_channel_delete(channel):
    # Enter when a VC Channel is deleted
    if isinstance(channel, discord.VoiceChannel):
        deleted_channel_id = channel.id

        # Check if the VC Channel belongs to a User
        for item in voice_channel_owners:
            if deleted_channel_id == item["VC_Channel_ID"]:
                print("Permanent VC: " + str(item["User_ID"]) + " deleted Voice Channel " + str(item["VC_Channel_ID"]))
                voice_channel_owners.remove(item)
                # Save the updated JSON data back to the file
                with open(file_path, "w") as json_file:
                    json.dump(voice_channel_owners, json_file, indent=4)
                break  # Exit the loop once the item is found

# Just for Testing
@bot.command(description="TEST")
async def vc_test(ctx):
        await ctx.respond(f"This is just an Test", ephemeral=True)


# Delete the permanent VC, when a User is leaving the Server
@bot.event
async def on_member_remove(member):
    # Check if the VC Channel belongs to a User
    for item in voice_channel_owners:
        if member.id == item["VC_Channel_ID"]:
            print("Permanent VC: " + str(item["User_ID"]) + " deleted Voice Channel " + str(item["VC_Channel_ID"]))
            voice_channel_owners.remove(item)
            # Save the updated JSON data back to the file
            with open(file_path, "w") as json_file:
                json.dump(voice_channel_owners, json_file, indent=4)
            break  # Exit the loop once the item is found




bot.run(config.TOKEN)