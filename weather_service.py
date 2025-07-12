"""
Weather Service
Handles OpenWeatherMap API integration and data processing.
"""

import aiohttp
import asyncio
import os
from datetime import datetime
from typing import Dict, Any

class WeatherService:
    """Service class for fetching weather data from OpenWeatherMap API."""
    
    def __init__(self):
        """Initialize the weather service with API configuration."""
        self.api_key = os.getenv('OPENWEATHER_API_KEY', '84111a9b5f081eb71e215fe10dc34bcd')
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.session = None
    
    async def get_session(self):
        """Get or create an aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            )
        return self.session
    
    async def close_session(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_weather(self, location: str) -> Dict[str, Any]:
        """
        Fetch current weather data for a given location.
        
        Args:
            location: City name, city+country, or coordinates
            
        Returns:
            Dictionary containing processed weather data
            
        Raises:
            ValueError: If location is not found
            ConnectionError: If API request fails
        """
        params = {
            'q': location,
            'appid': self.api_key,
            'units': 'metric'  # Use metric units (Celsius, m/s, etc.)
        }
        
        session = await self.get_session()
        
        try:
            async with session.get(self.base_url, params=params) as response:
                if response.status == 404:
                    raise ValueError(f"Location '{location}' not found")
                elif response.status == 401:
                    raise ConnectionError("Invalid API key")
                elif response.status == 429:
                    raise ConnectionError("API rate limit exceeded")
                elif response.status != 200:
                    raise ConnectionError(f"API request failed with status {response.status}")
                
                data = await response.json()
                return self.process_weather_data(data)
                
        except aiohttp.ClientError as e:
            raise ConnectionError(f"Failed to connect to weather service: {e}")
        except asyncio.TimeoutError:
            raise ConnectionError("Request timed out")
    
    def process_weather_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw API response into a clean format.
        
        Args:
            raw_data: Raw response from OpenWeatherMap API
            
        Returns:
            Processed weather data dictionary
        """
        main = raw_data.get('main', {})
        weather = raw_data.get('weather', [{}])[0]
        wind = raw_data.get('wind', {})
        sys_data = raw_data.get('sys', {})
        
        processed_data = {
            'location': raw_data.get('name', 'Unknown'),
            'country': sys_data.get('country', 'Unknown'),
            'description': weather.get('description', 'Unknown'),
            'temperature': round(main.get('temp', 0)),
            'feels_like': round(main.get('feels_like', 0)),
            'humidity': main.get('humidity', 0),
            'pressure': main.get('pressure', 0),
            'wind_speed': round(wind.get('speed', 0), 1),
            'wind_deg': wind.get('deg'),
            'visibility': round(raw_data.get('visibility', 0) / 1000, 1),  # Convert to km
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        }
        
        return processed_data
    
    def __del__(self):
        """Cleanup when the service is destroyed."""
        if hasattr(self, 'session') and self.session and not self.session.closed:
            # Create a new event loop if one doesn't exist
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, schedule the cleanup
                    loop.create_task(self.close_session())
                else:
                    # If loop is not running, run the cleanup
                    loop.run_until_complete(self.close_session())
            except RuntimeError:
                # If no event loop exists, create one for cleanup
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.close_session())
                loop.close()
