import os
import googlemaps
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv
import json
import re

load_dotenv()
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))
output_filename = os.getenv("PROMPT_INPUT_FILENAME")

def estimate_battery_drain(distance_miles, drain_per_mile=0.5):
    return round(distance_miles * drain_per_mile, 1)
    
    
def get_commute_estimate(origin, destination, departure_time=None):
    if not departure_time:
        departure_time = datetime.now()

    result = gmaps.distance_matrix(
        origins=origin,
        destinations=destination,
        departure_time=departure_time,
        units="imperial",
        traffic_model="best_guess"
    )

    duration_in_traffic = result["rows"][0]["elements"][0]["duration_in_traffic"]["text"]
    distance = result["rows"][0]["elements"][0]["distance"]["text"]
    # print(distance)
    
    return {
        "duration": duration_in_traffic,
        "distance": distance,
		"battery_drainage": estimate_battery_drain(float(distance.split(" ")[0]))
    }


def get_30_min_intervals(origin, destination):
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    start_time = tomorrow.replace(hour=8, minute=0, second=0, microsecond=0)

    intervals = [start_time + timedelta(minutes=30 * i) for i in range(7)]  # 8:00 to 11:00
    print("Retreiving...")
    results = []
    for departure_time in intervals:
        try:
            directions_result = gmaps.directions(
                origin,
                destination,
                mode="driving",
                departure_time=departure_time,
                traffic_model="best_guess",
                alternatives=True
            )
            if not directions_result:
                results.append({
                    "departure_time": departure_time,
                    "duration_in_traffic": None,
                    "distance":None,
                    "route_freeways": None,
                    "error": "No results"
                })
                continue
                
            for route in directions_result:
                leg = route["legs"][0]
                duration_in_traffic = leg["duration_in_traffic"]["text"]
                distance_ = leg["distance"]["text"]
                
                
                ## Extract freeway info
                freeways = []
                for step in leg["steps"]:
                    instr = step.get("html_instructions", "")
                    frwy = re.findall(r"\b(?:I|US|CA)[- ]?\d+\b", instr)
                    freeways.extend(frwy)
                        
                # Deduplicate while keeping order
                seen, ordered = set(), []
                for h in freeways:
                    if h not in seen:
                        seen.add(h)
                        ordered.append(h)

                results.append({
                    "departure_time": departure_time,
                    "duration_in_traffic": duration_in_traffic,
                    "distance":distance_,
                    "route_freeways": ordered,
                    "error": None
                })

            time.sleep(1)  # to avoid rate limits

        except Exception as e:
            results.append({
                "departure_time": departure_time,
                "duration_in_traffic": None,
                "distance":None,
                "route_freeways": None,
                "error": str(e)
            })
    # print(results)
    return results

def maps_api_call():

	estimate = get_commute_estimate(os.getenv("ORIGIN_ADDRESS"), os.getenv("DEST_ADDRESS"))
#	print(estimate)

	traffic_data = get_30_min_intervals(os.getenv("ORIGIN_ADDRESS"), os.getenv("DEST_ADDRESS"))
#	for entry in traffic_data:
#			dt_str = entry["departure_time"].strftime("%Y-%m-%d %I:%M %p")
#			if entry["error"]:
#				print(f"{dt_str} - Error: {entry['error']}")
#			else:
#				print(f"{dt_str} - Duration in traffic: {entry['duration_in_traffic']}")

	output_object = {"commute_distance": estimate['distance'], "minimum_battery_drainage": estimate['battery_drainage']}
	
	times_to_commute = []
	
	for entry in traffic_data:
		dt = entry["departure_time"].strftime("%Y-%m-%d %I:%M %p")
		duration_mins = entry['duration_in_traffic']
		route_distance = entry["distance"]
		route_info = entry["route_freeways"]
		times_to_commute.append({"departure_datetime": dt, "commute_duration": duration_mins, "route_info": route_info, "route_distance": route_distance})

	output_object['commute_options'] = times_to_commute
	
	with open(output_filename, "r") as f:
		data = json.load(f)
		
	data["traffic_data"] = output_object
	
	with open(output_filename, "w") as f:
		json.dump(data, f, indent=4)
#		
#def main():
#    maps_api_call()
#    
#if __name__ == '__main__':
#	main()
