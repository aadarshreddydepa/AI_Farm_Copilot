import os
import requests
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AGRO_API_KEY = os.getenv("AGRO_API_KEY")
PLANT_ID_API_KEY = os.getenv("PLANT_ID_API_KEY")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIFetcher:
    def __init__(self):
        if not OPENWEATHER_API_KEY:
            raise ValueError("Missing OPENWEATHER_API_KEY in .env file")
        if not AGRO_API_KEY:
            logger.warning("AGRO_API_KEY not found – AgroMonitoring API features will not work.")
        if not PLANT_ID_API_KEY:
            logger.warning("PLANT_ID_API_KEY not found – Plant Identification features will not work.")

    # ---------------------------
    # 🌍 Weather + Geocoding
    # ---------------------------
    def get_coordinates(self, location: str) -> Optional[Dict[str, float]]:
        """Convert location name into latitude & longitude using OpenWeather Geocoding API"""
        try:
            url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={OPENWEATHER_API_KEY}"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if not data:
                logger.warning(f"No coordinates found for {location}")
                return None

            return {"lat": data[0]["lat"], "lon": data[0]["lon"]}
        except Exception as e:
            logger.error(f"Error fetching coordinates: {str(e)}")
            return None

    def get_weather(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Fetch current weather for given coordinates"""
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Error fetching weather: {str(e)}")
            return None

    # ---------------------------
    # 🛰 AgroMonitoring API
    # ---------------------------
    def get_agro_data(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Fetch NDVI/soil/crop data for given location using AgroMonitoring API"""
        if not AGRO_API_KEY:
            logger.error("AgroMonitoring API key missing")
            return None

        try:
            # Example: soil data endpoint
            url = f"http://api.agromonitoring.com/agro/1.0/soil?lat={lat}&lon={lon}&appid={AGRO_API_KEY}"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Error fetching agro data: {str(e)}")
            return None

    # ---------------------------
    # 🌱 Plant Identification API
    # ---------------------------
    def identify_plant(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Identify plant or pest using Plant.id API"""
        if not PLANT_ID_API_KEY:
            logger.error("Plant.id API key missing")
            return None

        try:
            url = "https://api.plant.id/v2/identify"
            headers = {"Api-Key": PLANT_ID_API_KEY}
            
            files = [("images", open(image_path, "rb"))]
            data = {
                "organs": ["leaf", "flower", "fruit"],
            }

            resp = requests.post(url, headers=headers, files=files, data=data, timeout=20)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Error identifying plant: {str(e)}")
            return None


# Example usage
if __name__ == "__main__":
    fetcher = APIFetcher()

    # 1️⃣ Get coordinates + weather
    coords = fetcher.get_coordinates("Akkampally")
    if coords:
        print("Coordinates:", coords)
        weather = fetcher.get_weather(coords["lat"], coords["lon"])
        print("Weather:", weather)
        # 2️⃣ Agro data
        agro_data = fetcher.get_agro_data(coords["lat"], coords["lon"])
        print("Agro Data:", agro_data)

    # 3️⃣ Plant identification (needs an image file)
    # plant_info = fetcher.identify_plant("test_leaf.jpg")
    # print("Plant Identification:", plant_info)
