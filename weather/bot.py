#!/usr/bin/env python3
"""
Discord Weather Bot - Working Version
"""

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from weather_service import WeatherService

# Load environment variables
load_dotenv()

# Create bot with proper intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Initialize weather service
weather_service = WeatherService()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guild(s)')
    print(f'Commands: {[cmd.name for cmd in bot.commands]}')

@bot.command(aliases=['we'])
async def weather(ctx, *, location: str = None):
    """Get weather information for a location"""
    print(f"Weather command called with location: {location}")
    
    if not location:
        embed = discord.Embed(
            title="❌ Missing Location",
            description="Please provide a location!\n\n**Usage:** `!weather <location>`\n**Example:** `!weather Berlin`",
            color=0xFF6B6B
        )
        await ctx.send(embed=embed)
        return
    
    async with ctx.typing():
        try:
            weather_data = await weather_service.get_weather(location)
            embed = create_weather_embed(weather_data)
            await ctx.send(embed=embed)
            
        except ValueError:
            embed = discord.Embed(
                title="📍 Location Not Found",
                description=f"Could not find weather data for **{location}**.\n\nPlease check the spelling and try again.",
                color=0xFF6B6B
            )
            await ctx.send(embed=embed)
            
        except ConnectionError:
            embed = discord.Embed(
                title="🌐 Connection Error",
                description="Unable to connect to weather service. Please try again later.",
                color=0xFF6B6B
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="⚠️ Error",
                description="An unexpected error occurred while fetching weather data. Please try again.",
                color=0xFF6B6B
            )
            await ctx.send(embed=embed)
            print(f"Unexpected error: {e}")

def create_weather_embed(weather_data):
    """Create a formatted Discord embed with weather information."""
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
    
    description = weather_data['description'].lower()
    emoji = weather_emojis.get(description, '🌤️')
    
    embed = discord.Embed(
        title=f"{emoji} Weather in {weather_data['location']}",
        description=weather_data['description'].title(),
        color=0x4A90E2
    )
    
    embed.add_field(
        name="🌡️ Temperature",
        value=f"**{weather_data['temperature']}°C**\nFeels like {weather_data['feels_like']}°C",
        inline=True
    )
    
    embed.add_field(
        name="💧 Humidity",
        value=f"{weather_data['humidity']}%",
        inline=True
    )
    
    wind_direction = get_wind_direction(weather_data['wind_deg'])
    embed.add_field(
        name="💨 Wind",
        value=f"{weather_data['wind_speed']} m/s {wind_direction}",
        inline=True
    )
    
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
    
    country_flag = get_country_flag(weather_data['country'])
    embed.add_field(
        name="🗺️ Country",
        value=f"{country_flag} {weather_data['country']}",
        inline=True
    )
    
    embed.set_footer(
        text=f"Provided by Emil • {weather_data['timestamp']}",
        icon_url="https://openweathermap.org/img/wn/01d@2x.png"
    )
    
    return embed

def get_wind_direction(degrees):
    """Convert wind degrees to cardinal direction."""
    if degrees is None:
        return ""
    
    directions = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
    ]
    
    index = round(degrees / 22.5) % 16
    return directions[index]

def get_country_flag(country_code):
    """Convert country code to flag emoji."""
    if not country_code or len(country_code) != 2:
        return "🏳️"
    
    flag_offset = ord('🇦') - ord('A')
    flag = ''.join(chr(ord(char) + flag_offset) for char in country_code.upper())
    return flag

@bot.command()
async def help(ctx):
    """Display help information"""
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

if __name__ == "__main__":
    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not bot_token:
        print("Error: DISCORD_BOT_TOKEN environment variable is required")
        exit(1)
    
    print("Starting Discord Weather Bot...")
    bot.run(bot_token)