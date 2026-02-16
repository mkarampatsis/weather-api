import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": [34.7768, 34.9221, 34.6841, 34.7768],
	"longitude": [32.4245, 33.6279, 33.0379, 32.4245],
	"daily": ["temperature_2m_max", "temperature_2m_min", "sunrise", "sunset", "daylight_duration", "sunshine_duration", "weather_code"],
	"hourly": ["temperature_2m", "rain", "showers", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "relative_humidity_2m", "weather_code"],
	"current": ["temperature_2m", "relative_humidity_2m", "rain", "showers", "weather_code"],
	"timezone": "Africa/Cairo",
}
responses = openmeteo.weather_api(url, params=params)

# Process 4 locations
for response in responses:
	print(f"\nCoordinates: {response.Latitude()}°N {response.Longitude()}°E")
	print(f"Elevation: {response.Elevation()} m asl")
	print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
	print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")
	
	# Process current data. The order of variables needs to be the same as requested.
	current = response.Current()
	current_temperature_2m = current.Variables(0).Value()
	current_relative_humidity_2m = current.Variables(1).Value()
	current_rain = current.Variables(2).Value()
	current_showers = current.Variables(3).Value()
	current_weather_code = current.Variables(4).Value()
	
	print(f"\nCurrent time: {current.Time()}")
	print(f"Current temperature_2m: {current_temperature_2m}")
	print(f"Current relative_humidity_2m: {current_relative_humidity_2m}")
	print(f"Current rain: {current_rain}")
	print(f"Current showers: {current_showers}")
	print(f"Current weather_code: {current_weather_code}")
	
	# Process hourly data. The order of variables needs to be the same as requested.
	hourly = response.Hourly()
	hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
	hourly_rain = hourly.Variables(1).ValuesAsNumpy()
	hourly_showers = hourly.Variables(2).ValuesAsNumpy()
	hourly_cloud_cover = hourly.Variables(3).ValuesAsNumpy()
	hourly_cloud_cover_low = hourly.Variables(4).ValuesAsNumpy()
	hourly_cloud_cover_mid = hourly.Variables(5).ValuesAsNumpy()
	hourly_cloud_cover_high = hourly.Variables(6).ValuesAsNumpy()
	hourly_relative_humidity_2m = hourly.Variables(7).ValuesAsNumpy()
	hourly_weather_code = hourly.Variables(8).ValuesAsNumpy()
	
	hourly_data = {"date": pd.date_range(
		start = pd.to_datetime(hourly.Time() + response.UtcOffsetSeconds(), unit = "s", utc = True),
		end =  pd.to_datetime(hourly.TimeEnd() + response.UtcOffsetSeconds(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = hourly.Interval()),
		inclusive = "left"
	)}
	
	hourly_data["temperature_2m"] = hourly_temperature_2m
	hourly_data["rain"] = hourly_rain
	hourly_data["showers"] = hourly_showers
	hourly_data["cloud_cover"] = hourly_cloud_cover
	hourly_data["cloud_cover_low"] = hourly_cloud_cover_low
	hourly_data["cloud_cover_mid"] = hourly_cloud_cover_mid
	hourly_data["cloud_cover_high"] = hourly_cloud_cover_high
	hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
	hourly_data["weather_code"] = hourly_weather_code
	
	hourly_dataframe = pd.DataFrame(data = hourly_data)
	print("\nHourly data\n", hourly_dataframe)
	
	# Process daily data. The order of variables needs to be the same as requested.
	daily = response.Daily()
	daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
	daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
	daily_sunrise = daily.Variables(2).ValuesInt64AsNumpy()
	daily_sunset = daily.Variables(3).ValuesInt64AsNumpy()
	daily_daylight_duration = daily.Variables(4).ValuesAsNumpy()
	daily_sunshine_duration = daily.Variables(5).ValuesAsNumpy()
	daily_weather_code = daily.Variables(6).ValuesAsNumpy()
	
	daily_data = {"date": pd.date_range(
		start = pd.to_datetime(daily.Time() + response.UtcOffsetSeconds(), unit = "s", utc = True),
		end =  pd.to_datetime(daily.TimeEnd() + response.UtcOffsetSeconds(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = daily.Interval()),
		inclusive = "left"
	)}
	
	daily_data["temperature_2m_max"] = daily_temperature_2m_max
	daily_data["temperature_2m_min"] = daily_temperature_2m_min
	daily_data["sunrise"] = daily_sunrise
	daily_data["sunset"] = daily_sunset
	daily_data["daylight_duration"] = daily_daylight_duration
	daily_data["sunshine_duration"] = daily_sunshine_duration
	daily_data["weather_code"] = daily_weather_code
	
	daily_dataframe = pd.DataFrame(data = daily_data)
	print("\nDaily data\n", daily_dataframe)
	