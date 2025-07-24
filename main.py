# main.py
from utils.get_weather_data import weather_api_calls
from utils.get_maps_data import maps_api_call
from utils.get_tesla_data import make_tesla_api_calls
from utils.get_claude_response import call_claude_api
from utils.send_email_response import send_email

def run_commute_briefer():

	# Step 1: Get Tesla data
	print("Fetching Tesla Data....")
	tesla_data = make_tesla_api_calls()

	# Step 2: Get weather data
	print("<---------------------------->")
	print("Fetching Weather Data....")
	weather_data = weather_api_calls()
	
	# Step 3: Get Maps data
	print("<---------------------------->")
	print("Fetching Traffic Data....")
	maps_data = maps_api_call()
	
	# Step 4: Generate LLM Response
	print("<---------------------------->")
	print("Generating Claude Response....")
	print("<---------------------------->")
	claude_response = call_claude_api()


	print("Sending Email Update...")
	send_email()

if __name__ == "__main__":
    run_commute_briefer()
