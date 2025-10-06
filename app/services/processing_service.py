import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from api_fetcher import APIFetcher

logger = logging.getLogger(__name__)


class TemperatureRange(Enum):
    """Temperature thresholds for crop management"""
    COLD_THRESHOLD = 15
    HOT_THRESHOLD = 35


class MoistureRange(Enum):
    """Soil moisture thresholds"""
    DRY_THRESHOLD = 0.2
    WET_THRESHOLD = 0.8


@dataclass
class WeatherInsight:
    """Structure for weather-related insights"""
    temperature: Optional[float]
    condition: str
    rainfall: float
    advice: str


@dataclass
class SoilInsight:
    """Structure for soil-related insights"""
    moisture: Optional[float]
    nitrogen: Optional[float]
    advice: str


@dataclass
class PlantInsight:
    """Structure for plant identification insights"""
    identified_as: str
    confidence: float
    care_tips: Optional[List[str]] = None


class ProcessingService:
    """
    Service for analyzing agricultural data from multiple sources
    and generating actionable insights for farmers.
    """
    
    def __init__(self, 
                 cold_threshold: float = TemperatureRange.COLD_THRESHOLD.value,
                 hot_threshold: float = TemperatureRange.HOT_THRESHOLD.value,
                 dry_threshold: float = MoistureRange.DRY_THRESHOLD.value,
                 wet_threshold: float = MoistureRange.WET_THRESHOLD.value):
        """
        Initialize the processing service with configurable thresholds.
        
        Args:
            cold_threshold: Temperature below which crops need protection
            hot_threshold: Temperature above which irrigation is critical
            dry_threshold: Soil moisture level below which irrigation is needed
            wet_threshold: Soil moisture level above which to reduce irrigation
        """
        self.cold_threshold = cold_threshold
        self.hot_threshold = hot_threshold
        self.dry_threshold = dry_threshold
        self.wet_threshold = wet_threshold
        logger.info("ProcessingService initialized with custom thresholds")

    def analyze_data(
        self, 
        weather_data: Optional[Dict[str, Any]] = None, 
        agro_data: Optional[Dict[str, Any]] = None, 
        plant_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Combine and analyze data from APIs to form actionable insights.
        
        Args:
            weather_data: Weather information from OpenWeather API
            agro_data: Soil and agricultural data from AgroMonitoring API
            plant_info: Plant identification data from Plant.id or similar
            
        Returns:
            Dictionary containing analyzed insights and recommendations
        """
        try:
            insights = {
                "status": "success",
                "timestamp": None,  # Could add datetime.now() if needed
                "data_sources": self._get_available_sources(weather_data, agro_data, plant_info)
            }
            
            # Analyze each data source
            if weather_data:
                weather_insight = self._analyze_weather(weather_data)
                if weather_insight:
                    insights["weather"] = weather_insight
            
            if agro_data:
                soil_insight = self._analyze_soil(agro_data)
                if soil_insight:
                    insights["soil"] = soil_insight
            
            if plant_info:
                plant_insight = self._analyze_plant(plant_info)
                if plant_insight:
                    insights["plant"] = plant_insight
            
            # Generate combined recommendations
            insights["combined_recommendations"] = self._generate_combined_recommendations(
                insights.get("weather"),
                insights.get("soil"),
                insights.get("plant")
            )
            
            return insights
            
        except Exception as e:
            logger.error(f"Error in processing data: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__
            }

    def _get_available_sources(self, 
                               weather_data: Optional[Dict], 
                               agro_data: Optional[Dict], 
                               plant_info: Optional[Dict]) -> List[str]:
        """Identify which data sources are available"""
        sources = []
        if weather_data:
            sources.append("weather")
        if agro_data:
            sources.append("soil")
        if plant_info:
            sources.append("plant")
        return sources

    def _analyze_weather(self, weather_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze weather data and provide recommendations.
        
        Args:
            weather_data: Weather information dictionary
            
        Returns:
            Dictionary with weather insights and advice
        """
        try:
            main = weather_data.get("main", {})
            weather_list = weather_data.get("weather", [{}])
            rain = weather_data.get("rain", {})
            
            temp = main.get("temp")
            feels_like = main.get("feels_like")
            humidity = main.get("humidity")
            condition = weather_list[0].get("description", "unknown") if weather_list else "unknown"
            rainfall = rain.get("1h", 0)
            
            # Generate temperature-based advice
            advice = self._get_temperature_advice(temp)
            
            # Add humidity-based advice
            if humidity and humidity > 80:
                advice += " High humidity may increase disease risk."
            elif humidity and humidity < 30:
                advice += " Low humidity may stress plants."
            
            return {
                "temperature": temp,
                "feels_like": feels_like,
                "humidity": humidity,
                "condition": condition,
                "rainfall": rainfall,
                "advice": advice.strip()
            }
            
        except Exception as e:
            logger.warning(f"Error analyzing weather data: {str(e)}")
            return None

    def _get_temperature_advice(self, temp: Optional[float]) -> str:
        """Generate advice based on temperature"""
        if not temp:
            return "Temperature data unavailable."
        
        if temp < self.cold_threshold:
            return "Cold conditions detected. Protect sensitive crops and consider frost protection measures."
        elif temp > self.hot_threshold:
            return "High temperature alert. Ensure adequate irrigation and consider shade for sensitive plants."
        else:
            return "Temperature is favorable for most crops."

    def _analyze_soil(self, agro_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze soil data and provide recommendations.
        
        Args:
            agro_data: Soil and agricultural data dictionary
            
        Returns:
            Dictionary with soil insights and advice
        """
        try:
            soil_moisture = agro_data.get("moisture")
            # Various soil parameters (adjust keys based on actual API)
            nitrogen = agro_data.get("t0") or agro_data.get("nitrogen")
            temperature = agro_data.get("t10")  # Soil temperature
            
            advice = []
            
            # Moisture analysis
            if soil_moisture is not None:
                moisture_advice = self._get_moisture_advice(soil_moisture)
                advice.append(moisture_advice)
            
            # Soil temperature analysis
            if temperature is not None:
                if temperature < 10:
                    advice.append("Soil temperature is low, which may slow seed germination.")
                elif temperature > 30:
                    advice.append("Soil temperature is high, monitor for heat stress.")
            
            return {
                "moisture": soil_moisture,
                "nitrogen": nitrogen,
                "soil_temperature": temperature,
                "advice": " ".join(advice) if advice else "Soil conditions appear normal."
            }
            
        except Exception as e:
            logger.warning(f"Error analyzing soil data: {str(e)}")
            return None

    def _get_moisture_advice(self, moisture: float) -> str:
        """Generate advice based on soil moisture level"""
        if moisture < self.dry_threshold:
            return "Soil moisture is critically low. Immediate irrigation recommended."
        elif moisture > self.wet_threshold:
            return "Soil moisture is excessive. Reduce irrigation and ensure proper drainage."
        else:
            return "Soil moisture levels are optimal."

    def _analyze_plant(self, plant_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze plant identification data.
        
        Args:
            plant_info: Plant identification dictionary
            
        Returns:
            Dictionary with plant insights
        """
        try:
            suggestions = plant_info.get("suggestions", [])
            
            if not suggestions:
                return {
                    "identified_as": "Unknown",
                    "confidence": 0.0,
                    "message": "No plant identification matches found."
                }
            
            best_match = suggestions[0]
            plant_name = best_match.get("plant_name", "Unknown")
            probability = best_match.get("probability", 0.0)
            plant_details = best_match.get("plant_details", {})
            
            # Extract care tips if available
            care_tips = []
            if plant_details:
                if "watering" in plant_details:
                    care_tips.append(f"Watering: {plant_details['watering']}")
                if "sunlight" in plant_details:
                    care_tips.append(f"Sunlight: {plant_details['sunlight']}")
            
            result = {
                "identified_as": plant_name,
                "confidence": round(probability * 100, 2) if probability else 0.0,
                "confidence_level": self._get_confidence_level(probability)
            }
            
            if care_tips:
                result["care_tips"] = care_tips
            
            # Include alternative matches if confidence is low
            if probability < 0.7 and len(suggestions) > 1:
                alternatives = [
                    {
                        "name": s.get("plant_name", "Unknown"),
                        "confidence": round(s.get("probability", 0) * 100, 2)
                    }
                    for s in suggestions[1:4]  # Top 3 alternatives
                ]
                result["alternatives"] = alternatives
            
            return result
            
        except Exception as e:
            logger.warning(f"Error analyzing plant data: {str(e)}")
            return None

    def _get_confidence_level(self, probability: Optional[float]) -> str:
        """Classify confidence level"""
        if not probability:
            return "unknown"
        if probability >= 0.9:
            return "very high"
        elif probability >= 0.7:
            return "high"
        elif probability >= 0.5:
            return "moderate"
        else:
            return "low"

    def _generate_combined_recommendations(self,
                                          weather: Optional[Dict],
                                          soil: Optional[Dict],
                                          plant: Optional[Dict]) -> List[str]:
        """
        Generate combined recommendations based on all available data.
        
        Args:
            weather: Weather insights dictionary
            soil: Soil insights dictionary
            plant: Plant insights dictionary
            
        Returns:
            List of prioritized recommendations
        """
        recommendations = []
        
        # Critical weather + soil combination
        if weather and soil:
            temp = weather.get("temperature")
            moisture = soil.get("moisture")
            
            if temp and moisture is not None:
                if temp > self.hot_threshold and moisture < self.dry_threshold:
                    recommendations.append(
                        "🚨 URGENT: High temperature and low soil moisture detected. "
                        "Increase irrigation immediately to prevent crop stress."
                    )
                elif temp < self.cold_threshold and moisture > self.wet_threshold:
                    recommendations.append(
                        "⚠️ WARNING: Cold and wet conditions increase disease risk. "
                        "Ensure proper drainage and consider fungicide application."
                    )
        
        # Rainfall and moisture correlation
        if weather and soil:
            rainfall = weather.get("rainfall", 0)
            moisture = soil.get("moisture")
            
            if rainfall > 5 and moisture and moisture > self.wet_threshold:
                recommendations.append(
                    "Recent rainfall with high soil moisture. Skip irrigation and monitor for waterlogging."
                )
        
        # Plant-specific recommendations
        if plant and plant.get("confidence_level") in ["high", "very high"]:
            plant_name = plant.get("identified_as")
            recommendations.append(
                f"Plant identified as {plant_name}. Adjust care based on species-specific requirements."
            )
        
        if not recommendations:
            recommendations.append("Continue regular monitoring and maintenance schedules.")
        
        return recommendations