import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry
import json
import math

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": [35.1753, 34.6841, 34.9221, 34.7768, 35.0125, 34.6757, 38.1667, 34.7289, 35.0395],
	"longitude": [33.3642, 33.0379, 33.6279, 32.4245, 34.0583, 33.046, 23.7833, 33.3378, 33.9818],
	"hourly": ["temperature_2m", "relative_humidity_2m", "rain", "showers", "snowfall", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "visibility", "wind_speed_10m", "wind_speed_80m", "soil_temperature_0cm", "soil_temperature_6cm", "apparent_temperature"],
	"timezone": "Africa/Cairo",
	"forecast_days": 1,
}
cities = [
	{"name": "Nicosia", "lat": 35.1753, "lon": 33.3642},
	{"name": "Limassol", "lat": 34.6841, "lon": 33.0379},
	{"name": "Larnaca", "lat": 34.9221, "lon": 33.6279},
	{"name": "Paphos", "lat": 34.7768, "lon": 32.4245},
	{"name": "Protaras", "lat": 35.0125, "lon": 34.0583},
	{"name": "Agia Napa", "lat": 34.6757, "lon": 33.046},
	{"name": "Dhekelia", "lat": 38.1667, "lon": 23.7833},
	{"name": "Zygi", "lat": 34.7289, "lon": 33.3378},
	{"name": "Paralimni", "lat": 35.0395, "lon": 33.9818}
]
responses = openmeteo.weather_api(url, params=params)

result = []

def safe_str(value):
	return value.decode() if isinstance(value, bytes) else value

for idx, response in enumerate(responses):

	city_info = cities[idx]

	hourly = response.Hourly()

	# Extract all variables as numpy arrays
	temperature_2m = hourly.Variables(0).ValuesAsNumpy()
	relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
	rain = hourly.Variables(2).ValuesAsNumpy()
	showers = hourly.Variables(3).ValuesAsNumpy()
	snowfall = hourly.Variables(4).ValuesAsNumpy()
	cloud_cover = hourly.Variables(5).ValuesAsNumpy()
	cloud_cover_low = hourly.Variables(6).ValuesAsNumpy()
	cloud_cover_mid = hourly.Variables(7).ValuesAsNumpy()
	cloud_cover_high = hourly.Variables(8).ValuesAsNumpy()
	visibility = hourly.Variables(9).ValuesAsNumpy()
	wind_speed_10m = hourly.Variables(10).ValuesAsNumpy()
	wind_speed_80m = hourly.Variables(11).ValuesAsNumpy()
	soil_temperature_0cm = hourly.Variables(12).ValuesAsNumpy()
	soil_temperature_6cm = hourly.Variables(13).ValuesAsNumpy()
	apparent_temperature = hourly.Variables(14).ValuesAsNumpy()

	# Create datetime index
	dates = pd.date_range(
		start=pd.to_datetime(hourly.Time() + response.UtcOffsetSeconds(), unit="s", utc=True),
		periods=len(temperature_2m),
		freq=pd.Timedelta(seconds=hourly.Interval())
	)

	# Take first hour (index 0)
	i = 0

	city_weather = {
		"city": city_info["name"],  # ✅ Added city name
		"latitude": response.Latitude(),
		"longitude": response.Longitude(),
		"generationtime_ms": response.GenerationTimeMilliseconds(),
		"utc_offset_seconds": response.UtcOffsetSeconds(),
		"timezone": safe_str(response.Timezone()),
		"timezone_abbreviation": safe_str(response.TimezoneAbbreviation()),
		"elevation": response.Elevation(),
		"hourly_units": {
				"time": "iso8601",
				"temperature_2m": "°C",
				"relative_humidity_2m": "%",
				"rain": "mm",
				"showers": "mm",
				"snowfall": "cm",
				"cloud_cover": "%",
				"cloud_cover_low": "%",
				"cloud_cover_mid": "%",
				"cloud_cover_high": "%",
				"visibility": "m",
				"wind_speed_10m": "km/h",
				"wind_speed_80m": "km/h",
				"soil_temperature_0cm": "°C",
				"soil_temperature_6cm": "°C",
				"apparent_temperature": "°C"
		},
		"time": dates[i].isoformat(),
		"temperature_2m": float(temperature_2m[i]),
		"relative_humidity_2m": float(relative_humidity_2m[i]),
		"rain": float(rain[i]),
		"showers": float(showers[i]),
		"snowfall": float(snowfall[i]),
		"cloud_cover": float(cloud_cover[i]),
		"cloud_cover_low": float(cloud_cover_low[i]),
		"cloud_cover_mid": float(cloud_cover_mid[i]),
		"cloud_cover_high": float(cloud_cover_high[i]),
		"visibility": float(visibility[i]),
		"wind_speed_10m": float(wind_speed_10m[i]),
		"wind_speed_80m": float(wind_speed_80m[i]),
		"soil_temperature_0cm": float(soil_temperature_0cm[i]),
		"soil_temperature_6cm": float(soil_temperature_6cm[i]),
		"apparent_temperature": float(apparent_temperature[i]),
	}

	result.append(city_weather)

# Final JSON output
json_output = json.dumps(result, indent=2)
print(json_output)