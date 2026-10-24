# Discord Weather Bot

## Overview

A Discord bot that provides weather information to users through simple commands. The bot integrates with the OpenWeatherMap API to fetch real-time weather data and presents it in Discord channels using a clean command interface.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

- **Entry Point** (`main.py`): Handles bot initialization and graceful shutdown
- **Bot Logic** (`weather_bot.py`): Manages Discord interactions and command processing
- **Weather Service** (`weather_service.py`): Handles external API communication with OpenWeatherMap

## Key Components

### Discord Bot Core
- Built using `discord.py` library with command extensions
- Uses prefix-based commands (`!weather`)
- Implements proper Discord intents for message content access
- Custom bot status showing current functionality

### Weather Data Service
- Asynchronous HTTP client using `aiohttp` for API requests
- Configurable timeout settings (10 seconds)
- Session management for efficient connection reuse
- Error handling for API failures and invalid locations

### Configuration Management
- Environment variable-based configuration using `python-dotenv`
- Secure API key storage
- Fallback API key provided for development/testing

## Data Flow

1. User sends `!weather <location>` command in Discord
2. Bot processes command and extracts location parameter
3. Weather service makes HTTP request to OpenWeatherMap API
4. API response is processed and formatted
5. Formatted weather data is sent back to Discord channel

## External Dependencies

### APIs
- **OpenWeatherMap API**: Primary weather data source
  - Current weather endpoint
  - Supports city names, coordinates, and country codes
  - Requires API key authentication

### Python Libraries
- `discord.py`: Discord bot framework
- `aiohttp`: Async HTTP client for API requests
- `python-dotenv`: Environment variable management

## Deployment Strategy

### Environment Variables Required
- `DISCORD_BOT_TOKEN`: Discord bot authentication token
- `OPENWEATHER_API_KEY`: OpenWeatherMap API key (optional, has fallback)

### Runtime Requirements
- Python 3.7+
- Async/await support
- Internet connectivity for API access

### Error Handling
- Graceful shutdown on keyboard interrupt
- Comprehensive error logging
- API timeout and connection error handling
- Invalid location error responses

### Security Considerations
- Bot token stored securely in environment variables
- API key externalized from code
- Session management to prevent resource leaks
