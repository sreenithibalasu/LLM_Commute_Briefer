import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json



##configuration
load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")
output_filename = os.getenv("PROMPT_INPUT_FILENAME")

def get_weather_info(LATITUDE, LONGITUDE, UNITS = "imperial"):
	
	if not API_KEY:
		print("API Key Undefined")
		return
	
	
	api_url = "https://api.openweathermap.org/data/3.0/onecall?lat={}&lon={}&units={}&exclude=minutely,hourly,alerts&appid={}".format(LATITUDE, LONGITUDE, UNITS,API_KEY)
	# print(api_url)
	# try:
	response = requests.get(api_url)
	response.raise_for_status()
	data = response.json()
	
	# print(data)
	
	next_day_date = (datetime.now() + timedelta(days=1)).date()
	
	tomorrow_index = 1
	if len(data["daily"]) < 2:
		raise ValueError("Not enough daily data for tomorrow")
	
	
	entry = data["daily"][tomorrow_index]
	
	readable_date = datetime.fromtimestamp(entry["dt"]).strftime("%A, %B %d")
	temp_min = round(entry["temp"]["min"])
	temp_max = round(entry["temp"]["max"])
	description = entry["weather"][0]["description"]
	
	return {
		"date": readable_date,
			"min_temp": temp_min,
			"max_temp": temp_max,
			"description": description
}


def weather_api_calls():
	with open(output_filename, "r") as f:
		data = json.load(f)
	
	data["weather_data"] = {"origin": get_weather_info(float(os.getenv("ORIGIN_LATITUDE")), float(os.getenv("ORIGIN_LONGITUDE"))), "destination": get_weather_info(float(os.getenv("DEST_LATITUDE")), float(os.getenv("DEST_LONGITUDE")))}
	
	with open(output_filename, "w") as f:
		json.dump(data, f, indent=4)
	
