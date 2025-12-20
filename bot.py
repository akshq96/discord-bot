import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has logged in!')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

@bot.tree.command(name="analyze_server", description="Analyze the current server structure")
async def analyze_server(interaction: discord.Interaction):
    """Analyze the server and return its structure"""
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server!", ephemeral=True)
        return
    
    guild = interaction.guild
    
    # Collect server data
    server_data = {
        "server_name": guild.name,
        "server_id": str(guild.id),
        "owner": f"{guild.owner.name}#{guild.owner.discriminator}" if guild.owner else "Unknown",
        "member_count": guild.member_count,
        "created_at": guild.created_at.isoformat(),
        "channels": {
            "text_channels": len(guild.text_channels),
            "voice_channels": len(guild.voice_channels),
            "categories": len(guild.categories),
            "total": len(guild.channels)
        },
        "roles": len(guild.roles),
        "emojis": len(guild.emojis),
        "boost_level": guild.premium_tier,
        "boost_count": guild.premium_subscription_count
    }
    
    # Format response
    embed = discord.Embed(
        title=f"Server Analysis: {guild.name}",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Owner", value=server_data["owner"], inline=True)
    embed.add_field(name="Members", value=str(server_data["member_count"]), inline=True)
    embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="Text Channels", value=str(server_data["channels"]["text_channels"]), inline=True)
    embed.add_field(name="Voice Channels", value=str(server_data["channels"]["voice_channels"]), inline=True)
    embed.add_field(name="Categories", value=str(server_data["channels"]["categories"]), inline=True)
    embed.add_field(name="Roles", value=str(server_data["roles"]), inline=True)
    embed.add_field(name="Emojis", value=str(server_data["emojis"]), inline=True)
    embed.add_field(name="Boost Level", value=f"Level {server_data['boost_level']}", inline=True)
    
    await interaction.response.send_message(embed=embed)
    
    # Send detailed channel list
    channel_list = "**Channel List:**\n"
    for category in sorted(guild.categories, key=lambda x: x.position):
        channel_list += f"\n📁 **{category.name}**\n"
        for channel in sorted(category.channels, key=lambda x: x.position):
            if isinstance(channel, discord.TextChannel):
                channel_list += f"  💬 {channel.mention} ({channel.topic or 'No topic'})\n"
            elif isinstance(channel, discord.VoiceChannel):
                channel_list += f"  🔊 {channel.name}\n"
    
    # Add uncategorized channels
    uncategorized = [ch for ch in guild.channels if ch.category is None]
    if uncategorized:
        channel_list += "\n**Uncategorized:**\n"
        for channel in uncategorized:
            if isinstance(channel, discord.TextChannel):
                channel_list += f"  💬 {channel.mention}\n"
            elif isinstance(channel, discord.VoiceChannel):
                channel_list += f"  🔊 {channel.name}\n"
    
    if len(channel_list) > 2000:
        # Split into multiple messages if too long
        parts = [channel_list[i:i+2000] for i in range(0, len(channel_list), 2000)]
        for part in parts:
            await interaction.followup.send(part)
    else:
        await interaction.followup.send(channel_list)

@bot.tree.command(name="analyze_user", description="Get detailed information about a specific user")
async def analyze_user(interaction: discord.Interaction, user: discord.Member = None):
    """Analyze a specific user in the server"""
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server!", ephemeral=True)
        return
    
    target_user = user or interaction.user
    
    # Collect user data
    user_data = {
        "username": f"{target_user.name}#{target_user.discriminator}",
        "display_name": target_user.display_name,
        "user_id": str(target_user.id),
        "account_created": target_user.created_at.isoformat(),
        "joined_server": target_user.joined_at.isoformat() if target_user.joined_at else "Unknown",
        "roles": [role.name for role in target_user.roles if role.name != "@everyone"],
        "top_role": target_user.top_role.name if target_user.top_role else "None",
        "is_bot": target_user.bot,
        "is_booster": target_user.premium_since is not None,
        "avatar_url": str(target_user.display_avatar.url),
        "status": str(target_user.status),
        "activities": []
    }
    
    # Get activities
    for activity in target_user.activities:
        if activity:
            activity_info = {
                "type": str(activity.type).split('.')[-1],
                "name": activity.name
            }
            if hasattr(activity, 'details'):
                activity_info["details"] = activity.details
            user_data["activities"].append(activity_info)
    
    # Create embed
    embed = discord.Embed(
        title=f"User Analysis: {user_data['display_name']}",
        color=target_user.color if target_user.color.value != 0 else discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    embed.set_thumbnail(url=user_data["avatar_url"])
    embed.add_field(name="Username", value=user_data["username"], inline=True)
    embed.add_field(name="User ID", value=user_data["user_id"], inline=True)
    embed.add_field(name="Bot", value="Yes" if user_data["is_bot"] else "No", inline=True)
    embed.add_field(name="Account Created", value=target_user.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Joined Server", value=target_user.joined_at.strftime("%Y-%m-%d %H:%M:%S") if target_user.joined_at else "Unknown", inline=True)
    embed.add_field(name="Status", value=user_data["status"].title(), inline=True)
    embed.add_field(name="Top Role", value=user_data["top_role"], inline=True)
    embed.add_field(name="Server Booster", value="Yes" if user_data["is_booster"] else "No", inline=True)
    embed.add_field(name="Role Count", value=str(len(user_data["roles"])), inline=True)
    
    if user_data["roles"]:
        roles_text = ", ".join(user_data["roles"][:10])
        if len(user_data["roles"]) > 10:
            roles_text += f" (+{len(user_data['roles']) - 10} more)"
        embed.add_field(name="Roles", value=roles_text, inline=False)
    
    if user_data["activities"]:
        activities_text = "\n".join([f"• {act['name']} ({act['type']})" for act in user_data["activities"]])
        embed.add_field(name="Activities", value=activities_text, inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="scrape_user_messages", description="Scrape messages from a user in a specific channel")
@app_commands.describe(
    user="The user to scrape messages from",
    channel="The channel to search in (defaults to current channel)",
    limit="Number of messages to retrieve (max 100)"
)
async def scrape_user_messages(
    interaction: discord.Interaction,
    user: discord.Member,
    channel: discord.TextChannel = None,
    limit: int = 50
):
    """Scrape messages from a specific user in a channel"""
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server!", ephemeral=True)
        return
    
    target_channel = channel or interaction.channel
    limit = min(max(1, limit), 100)  # Clamp between 1 and 100
    
    await interaction.response.defer(ephemeral=True)
    
    # Collect messages
    messages_data = []
    message_count = 0
    
    try:
        async for message in target_channel.history(limit=limit * 2):  # Fetch more to filter
            if message.author.id == user.id and not message.author.bot:
                messages_data.append({
                    "content": message.content,
                    "timestamp": message.created_at.isoformat(),
                    "message_id": str(message.id),
                    "attachments": len(message.attachments),
                    "embeds": len(message.embeds),
                    "reactions": len(message.reactions)
                })
                message_count += 1
                if message_count >= limit:
                    break
    except discord.Forbidden:
        await interaction.followup.send("I don't have permission to read messages in this channel!", ephemeral=True)
        return
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)
        return
    
    if not messages_data:
        await interaction.followup.send(f"No messages found from {user.mention} in {target_channel.mention}", ephemeral=True)
        return
    
    # Create summary
    total_attachments = sum(msg["attachments"] for msg in messages_data)
    total_embeds = sum(msg["embeds"] for msg in messages_data)
    total_reactions = sum(msg["reactions"] for msg in messages_data)
    
    embed = discord.Embed(
        title=f"Message Scrape: {user.display_name}",
        description=f"Channel: {target_channel.mention}",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Messages Found", value=str(len(messages_data)), inline=True)
    embed.add_field(name="Total Attachments", value=str(total_attachments), inline=True)
    embed.add_field(name="Total Embeds", value=str(total_embeds), inline=True)
    embed.add_field(name="Total Reactions", value=str(total_reactions), inline=True)
    
    await interaction.followup.send(embed=embed, ephemeral=True)
    
    # Send message samples
    sample_text = f"**Sample Messages from {user.display_name}:**\n\n"
    for i, msg in enumerate(messages_data[:10], 1):
        timestamp = datetime.fromisoformat(msg["timestamp"]).strftime("%Y-%m-%d %H:%M")
        content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
        if not content:
            content = "[No text content]"
        sample_text += f"{i}. [{timestamp}] {content}\n"
        if msg["attachments"] > 0:
            sample_text += f"   📎 {msg['attachments']} attachment(s)\n"
        if msg["reactions"] > 0:
            sample_text += f"   ❤️ {msg['reactions']} reaction(s)\n"
        sample_text += "\n"
    
    if len(sample_text) > 2000:
        parts = [sample_text[i:i+2000] for i in range(0, len(sample_text), 2000)]
        for part in parts:
            await interaction.followup.send(part, ephemeral=True)
    else:
        await interaction.followup.send(sample_text, ephemeral=True)
    
    # Optionally save to file
    if len(messages_data) > 10:
        data_json = json.dumps(messages_data, indent=2)
        file = discord.File(
            fp=discord.utils.BytesIO(data_json.encode()),
            filename=f"user_messages_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        await interaction.followup.send("Full data exported to JSON file:", file=file, ephemeral=True)

@bot.tree.command(name="channel_stats", description="Get statistics about a specific channel")
async def channel_stats(interaction: discord.Interaction, channel: discord.TextChannel = None):
    """Get statistics about a channel"""
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server!", ephemeral=True)
        return
    
    target_channel = channel or interaction.channel
    
    await interaction.response.defer()
    
    # Collect channel data
    message_count = 0
    unique_authors = set()
    total_attachments = 0
    total_embeds = 0
    
    try:
        async for message in target_channel.history(limit=1000):
            message_count += 1
            unique_authors.add(message.author.id)
            total_attachments += len(message.attachments)
            total_embeds += len(message.embeds)
    except discord.Forbidden:
        await interaction.followup.send("I don't have permission to read messages in this channel!")
        return
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")
        return
    
    embed = discord.Embed(
        title=f"Channel Statistics: {target_channel.name}",
        color=discord.Color.purple(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Channel", value=target_channel.mention, inline=True)
    embed.add_field(name="Category", value=target_channel.category.name if target_channel.category else "None", inline=True)
    embed.add_field(name="Created", value=target_channel.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="Messages Analyzed", value=str(message_count), inline=True)
    embed.add_field(name="Unique Authors", value=str(len(unique_authors)), inline=True)
    embed.add_field(name="Total Attachments", value=str(total_attachments), inline=True)
    embed.add_field(name="Total Embeds", value=str(total_embeds), inline=True)
    embed.add_field(name="NSFW", value="Yes" if target_channel.nsfw else "No", inline=True)
    embed.add_field(name="Slowmode", value=f"{target_channel.slowmode_delay}s" if target_channel.slowmode_delay else "None", inline=True)
    
    if target_channel.topic:
        embed.add_field(name="Topic", value=target_channel.topic[:1024], inline=False)
    
    await interaction.followup.send(embed=embed)

# Run the bot
if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables!")
        print("Please create a .env file with: DISCORD_BOT_TOKEN=your_token_here")
    else:
        bot.run(token)

