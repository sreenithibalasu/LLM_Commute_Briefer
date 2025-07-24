import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
input_filename = os.getenv("PROMPT_INPUT_FILENAME")
output_filename = os.getenv("PROMPT_OUTPUT_FILENAME")

def generate_claude3_briefing(weather_info, tesla_info, commute_info):
    response = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=512,
        temperature=0.6,
        messages=[
            {
                "role": "user",
                "content": f"""
You're a friendly and cheerful daily commute assistant. Based on the information below, generate a short daily briefing that includes:
- what the weather is like and what to wear
- commute recommendation (when to leave, traffic, battery drain)
- car battery level and whether charging is needed

Weather: {weather_info}
Commute Info: {commute_info}
Tesla Status: {tesla_info}
"""
            }
        ]
    )

    return response.content[0].text

def call_claude_api():
	
	# Example
	with open(input_filename, "r") as f:
		data = json.load(f)
		

	weather = "Weather in Menlo Park: high of {}F and low of {} with description {}. Weather in South San Francisco: high of {}F and low of {} with description {}".format(data["weather_data"]["origin"]["min_temp"], data["weather_data"]["origin"]["max_temp"], data["weather_data"]["origin"]["description"],
	data["weather_data"]["destination"]["min_temp"], data["weather_data"]["destination"]["max_temp"], data["weather_data"]["destination"]["description"])
	tesla = "{}% battery remaining. Charging state: {} . Estimated range: {} miles.".format(data["tesla_status"]["battery_level"],data["tesla_status"]["charge_state"], data["tesla_status"]["battery_range"] )
	commute = "Commute Distance: {}, Minimum Battery Drainage: {}, Commute Options: {}".format(data["traffic_data"]["commute_distance"], data["traffic_data"]["minimum_battery_drainage"], data["traffic_data"]["commute_options"])


	with open(output_filename, "w") as f:
		json.dump({"claude_output": generate_claude3_briefing(weather, tesla, commute)}, f, indent=4)
		
	print(generate_claude3_briefing(weather, tesla, commute))
