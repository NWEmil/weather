"""
Discord Weather Bot - Simple Version
Handles Discord bot events and weather command processing.
"""

import discord
from discord.ext import commands
import asyncio
from weather_service import WeatherService

# Create bot instance
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    help_command=None
)

# Initialize weather service
weather_service = WeatherService()

@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord."""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guild(s)')
    
    # Debug: Print loaded commands
    print(f'Loaded commands: {[cmd.name for cmd in bot.commands]}')
    
    # Set bot status
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="weather patterns | !weather <location>"
    )
    await bot.change_presence(activity=activity)

@bot.event
async def on_message(message):
    """Process incoming messages."""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Debug: Log incoming messages that start with !
    if message.content.startswith('!'):
        print(f'Received command: {message.content}')
    
    # Process commands
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors."""
    if isinstance(error, commands.CommandNotFound):
        print(f'Command not found: {ctx.message.content}')
        # Don't send error message to user for unknown commands
        return
    else:
        print(f'Command error: {error}')
        await ctx.send(f'An error occurred: {error}')

@bot.command(name='weather')
async def weather_command(ctx, *, location: str = None):
    """
    Fetch and display current weather information for a location.
    
    Usage: !weather <location>
    Example: !weather Berlin
    """
    if not location:
        embed = discord.Embed(
            title="❌ Missing Location",
            description="Please provide a location!\n\n**Usage:** `!weather <location>`\n**Example:** `!weather Berlin`",
            color=0xFF6B6B
        )
        await ctx.send(embed=embed)
        return
    
    # Show typing indicator while fetching weather data
    async with ctx.typing():
        try:
            weather_data = await weather_service.get_weather(location)
            embed = create_weather_embed(weather_data)
            await ctx.send(embed=embed)
            
        except ValueError as e:
            # Location not found or invalid
            embed = discord.Embed(
                title="📍 Location Not Found",
                description=f"Could not find weather data for **{location}**.\n\nPlease check the spelling and try again.",
                color=0xFF6B6B
            )
            await ctx.send(embed=embed)
            
        except ConnectionError as e:
            # API connection issues
            embed = discord.Embed(
                title="🌐 Connection Error",
                description="Unable to connect to weather service. Please try again later.",
                color=0xFF6B6B
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            # General error handling
            embed = discord.Embed(
                title="⚠️ Error",
                description="An unexpected error occurred while fetching weather data. Please try again.",
                color=0xFF6B6B
            )
            await ctx.send(embed=embed)
            print(f"Unexpected error in weather command: {e}")

def create_weather_embed(weather_data):
    """Create a formatted Discord embed with weather information."""
    # Weather condition emojis
    weather_emojis = {
        'clear sky': '☀️',
        'few clouds': '🌤️',
        'scattered clouds': '⛅',
        'broken clouds': '☁️',
        'overcast clouds': '☁️',
        'shower rain': '🌦️',
        'rain': '🌧️',
        'thunderstorm': '⛈️',
        'snow': '❄️',
        'mist': '🌫️',
        'fog': '🌫️'
    }
    
    # Get appropriate emoji for weather condition
    description = weather_data['description'].lower()
    emoji = weather_emojis.get(description, '🌤️')
    
    # Create embed
    embed = discord.Embed(
        title=f"{emoji} Weather in {weather_data['location']}",
        description=weather_data['description'].title(),
        color=0x4A90E2
    )
    
    # Temperature field
    embed.add_field(
        name="🌡️ Temperature",
        value=f"**{weather_data['temperature']}°C**\nFeels like {weather_data['feels_like']}°C",
        inline=True
    )
    
    # Humidity field
    embed.add_field(
        name="💧 Humidity",
        value=f"{weather_data['humidity']}%",
        inline=True
    )
    
    # Wind field
    wind_direction = get_wind_direction(weather_data['wind_deg'])
    embed.add_field(
        name="💨 Wind",
        value=f"{weather_data['wind_speed']} m/s {wind_direction}",
        inline=True
    )
    
    # Additional weather info
    embed.add_field(
        name="👁️ Visibility",
        value=f"{weather_data['visibility']} km",
        inline=True
    )
    
    embed.add_field(
        name="🌊 Pressure",
        value=f"{weather_data['pressure']} hPa",
        inline=True
    )
    
    # Country flag emoji
    country_flag = get_country_flag(weather_data['country'])
    embed.add_field(
        name="🗺️ Country",
        value=f"{country_flag} {weather_data['country']}",
        inline=True
    )
    
    # Footer with timestamp
    embed.set_footer(
        text=f"Data from OpenWeatherMap • {weather_data['timestamp']}",
        icon_url="https://openweathermap.org/img/wn/01d@2x.png"
    )
    
    return embed

def get_wind_direction(degrees):
    """Convert wind degrees to cardinal direction."""
    if degrees is None:
        return ""
    
    directions = [
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW"
    ]
    
    # Calculate direction index
    index = round(degrees / 22.5) % 16
    return directions[index]

def get_country_flag(country_code):
    """Convert country code to flag emoji."""
    if not country_code or len(country_code) != 2:
        return "🏳️"
    
    # Convert country code to flag emoji
    flag_offset = ord('🇦') - ord('A')
    flag = ''.join(chr(ord(char) + flag_offset) for char in country_code.upper())
    return flag

@bot.command(name='help')
async def help_command(ctx):
    """Display help information for the weather bot."""
    embed = discord.Embed(
        title="🤖 Weather Bot Help",
        description="Get current weather information for any location!",
        color=0x4A90E2
    )
    
    embed.add_field(
        name="📋 Commands",
        value="`!weather <location>` - Get current weather\n`!help` - Show this help message",
        inline=False
    )
    
    embed.add_field(
        name="📝 Examples",
        value="`!weather Berlin`\n`!weather New York`\n`!weather Tokyo, JP`",
        inline=False
    )
    
    embed.add_field(
        name="💡 Tips",
        value="• You can use city names, city+country, or coordinates\n• Weather data includes temperature, humidity, wind, and more\n• All temperatures are shown in Celsius",
        inline=False
    )
    
    embed.set_footer(text="Weather data provided by OpenWeatherMap")
    
    await ctx.send(embed=embed)

# Function to run the bot
def run_bot(token):
    """Run the Discord bot."""
    bot.run(token)