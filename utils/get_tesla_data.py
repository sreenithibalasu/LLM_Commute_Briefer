import os
import requests
import json
import time
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()

CLIENT_ID = os.getenv("TESLA_CLIENT_ID")
CLIENT_SECRET = os.getenv("TESLA_CLIENT_SECRET")
REDIRECT_URI = os.getenv("TESLA_REDIRECT_URI")
TESLA_REGION = os.getenv("TESLA_REGION", "na") # default region North America

# Tesla API Endpoints
AUTH_BASE_URL = "https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token"
API_BASE_URL = f"https://fleet-api.prd.{TESLA_REGION}.vn.cloud.tesla.com/api/1"

# File to store current tokens (access_token, refresh_token, and their expiry time)
TOKEN_FILE = os.getenv("TOKEN_FILE")
output_filename = os.getenv("PROMPT_INPUT_FILENAME")

# --- Token Management Functions ---

def load_tokens():
    """Loads tokens from a local JSON file."""
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'r') as f:
                tokens = json.load(f)
                print(f"Tokens loaded from {TOKEN_FILE}.")
                return tokens
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {TOKEN_FILE}. File might be corrupted.")
            return None
    print(f"No tokens file found at {TOKEN_FILE}.")
    return None

def save_tokens(tokens):
    """Saves tokens to a local JSON file."""
    try:
        with open(TOKEN_FILE, 'w') as f:
            json.dump(tokens, f, indent=4)
        print(f"Tokens saved to {TOKEN_FILE}.")
    except IOError as e:
        print(f"Error saving tokens to {TOKEN_FILE}: {e}")

def refresh_access_token(current_refresh_token):
    """Refreshes the access token using the refresh token."""
    print("Attempting to refresh access token...")
    payload = {
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': current_refresh_token,
        'audience': API_BASE_URL.replace("/api/1", "") 
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        response = requests.post(AUTH_BASE_URL, data=payload, headers=headers)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        new_tokens = response.json()
        
        # Store the current time when the token was obtained for expiration checks
        new_tokens['obtained_at'] = int(time.time())
        print("Access token refreshed successfully.")
        return new_tokens
    except requests.exceptions.RequestException as e:
        print(f"Error refreshing token: {e}")
        if response is not None and response.text:
            print(f"Response content: {response.text}")
        return None

def get_valid_access_token():
    """
    Ensures a valid access token is available.
    Refreshes if expired or close to expiration.
    Handles initial token setup from .env if no token file exists.
    """
    tokens = load_tokens()

    # If no tokens file, try to use an initial refresh token from .env
    if not tokens:
        initial_refresh_token = os.getenv("TESLA_INITIAL_REFRESH_TOKEN")
        if initial_refresh_token:
            print("No token file found. Attempting to use initial refresh token from .env for first time setup.")
            tokens = refresh_access_token(initial_refresh_token)
            if tokens:
                save_tokens(tokens) # Save the newly obtained tokens
                return tokens['access_token']
            else:
                print("Failed to get initial tokens using TESLA_INITIAL_REFRESH_TOKEN. "
                      "Ensure it's correct and you have the 'offline_access' scope.")
                return None
        else:
            print("No tokens found and TESLA_INITIAL_REFRESH_TOKEN not set in .env. "
                  "Please perform initial browser authorization to get a refresh token.")
            return None

    # Check if existing access token is expired or close to expiration
    # Tesla tokens are usually 1 hour (3600 seconds), refresh if less than 5 minutes (300 seconds) remain
    if 'obtained_at' in tokens and 'expires_in' in tokens:
        current_time = int(time.time())
        if tokens['obtained_at'] + tokens['expires_in'] - current_time < 300: # 5 minutes buffer
            print("Access token is expiring soon or has expired.")
            new_tokens = refresh_access_token(tokens['refresh_token'])
            if new_tokens:
                save_tokens(new_tokens) # Save the new tokens (new refresh_token included)
                return new_tokens['access_token']
            else:
                print("Failed to refresh token. The refresh token might be invalid or expired. "
                      "Manual re-authorization may be required.")
                return None
    
    # If the access token is still valid
    print("Using existing valid access token.")
    return tokens['access_token']

# --- Vehicle Interaction Functions ---

def wake_up_vehicle(access_token, vehicle_id):
    """Sends a wake up command to the vehicle."""
    print(f"Attempting to wake up vehicle {vehicle_id}...")
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    url = f"{API_BASE_URL}/vehicles/{vehicle_id}/wake_up" 
    
    try:
        response = requests.post(url, headers=headers, data='{}')
        response.raise_for_status()
        print(f"Wake up command sent for vehicle {vehicle_id}.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending wake up command: {e}")
        if response is not None and response.text:
            print(f"Response content: {response.text}")
        return None

def get_vehicles(access_token):
    """Fetches the list of vehicles associated with the account."""
    print("Fetching list of vehicles...")
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    url = f"{API_BASE_URL}/vehicles"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        # print("Vehicle list fetched successfully.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching vehicles: {e}")
        if response is not None and response.text:
            print(f"Response: {response.text}")
        return None

def get_vehicle_data(access_token, vehicle_id, max_retries=5, initial_delay=8):
    """
    Fetches detailed vehicle data, with retry logic for 408 (Vehicle Offline) errors.
    
    Args:
        access_token (str): The current valid access token.
        vehicle_id (str): The ID of the vehicle to fetch data for.
        max_retries (int): Maximum number of attempts to fetch data.
        initial_delay (int): Initial delay in seconds before first retry after a wake-up.
                              Subsequent delays increase.
    """
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    url = f"{API_BASE_URL}/vehicles/{vehicle_id}/vehicle_data"

    for attempt in range(max_retries):
        print(f"Attempt {attempt + 1}/{max_retries} to fetch vehicle data for {vehicle_id}...")
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 408:
                print(f"Vehicle {vehicle_id} is offline/unavailable (HTTP 408). Attempting to wake up...")
                wake_up_response = wake_up_vehicle(access_token, vehicle_id)
                
                if wake_up_response:
                    # Implement increasing delay for retries
                    current_delay = initial_delay * (attempt + 1)
                    print(f"Wake-up command sent. Waiting {current_delay} seconds before retrying...")
                    time.sleep(current_delay)
                else:
                    print("Failed to send wake up command. Aborting further retries for data fetch.")
                    return None # Could not even send wake up command, no point in continuing
                
                continue # Go to the next attempt in the loop
            
            # If not 408, check for other errors or return success
            response.raise_for_status() # Will raise HTTPError for 4xx or 5xx status codes
            # print(f"Successfully fetched data for vehicle {vehicle_id}.")
            return response.json()

        except requests.exceptions.RequestException as e:
            # Catch general request errors (network, other HTTP errors)
            print(f"Request error fetching vehicle data (attempt {attempt + 1}): {e}")
            if response is not None and response.text:
                print(f"Full error response: {response.text}")
            
            # For non-408 errors, you might choose to exit immediately or retry
            # For simplicity, we'll exit after any non-408 error on the first try.
            return None # Exit function on other types of errors

    print(f"Failed to fetch vehicle data for {vehicle_id} after {max_retries} attempts due to persistent 408 errors or other issues.")
    return None

def send_vehicle_command(access_token, vehicle_id, command_name, command_data=None):
    """
    Sends a command to the Tesla vehicle.
    
    Args:
        access_token (str): The current valid access token.
        vehicle_id (str): The ID of the vehicle.
        command_name (str): The specific command endpoint (e.g., 'honk_horn', 'door_lock', 'charge_start').
        command_data (dict, optional): Dictionary of parameters for the command. Defaults to None (empty JSON).
    """
    print(f"\nAttempting to send '{command_name}' command to vehicle {vehicle_id}...")
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    url = f"{API_BASE_URL}/vehicles/{vehicle_id}/command/{command_name}"
    
    # Ensure command_data is an empty dict if None, as some commands need an empty JSON body
    payload = json.dumps(command_data if command_data is not None else {})

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status() # Raise an exception for bad status codes
        
        # Tesla command responses often have a 'response' object with 'result' (bool) and 'reason' (str)
        command_response = response.json()
        if 'response' in command_response and command_response['response'].get('result') is True:
            print(f"Command '{command_name}' sent successfully! Reason: {command_response['response'].get('reason', 'N/A')}")
        else:
            # Command was accepted by API but vehicle might have rejected it
            print(f"Command '{command_name}' failed at vehicle. API Response: {command_response.get('response', 'No specific response object')}")
        return command_response

    except requests.exceptions.RequestException as e:
        print(f"Error sending command '{command_name}': {e}")
        if response is not None and response.text:
            print(f"Full error response: {response.text}")
        return None
def make_tesla_api_calls():
	# 1. Get a valid access token (will refresh if needed, or use initial from .env)
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: TESLA_CLIENT_ID and TESLA_CLIENT_SECRET must be set in your .env file.")
        print("Please create a .env file with these variables and TESLA_INITIAL_REFRESH_TOKEN (after first manual auth).")
        exit(1)

    # 1. Get a valid access token (will refresh if needed, or use initial from .env)
    token = get_valid_access_token()

    if not token:
        print("Failed to get a valid access token. Cannot proceed with API calls.")
        exit(1)
	# 2. List vehicles to get the ID of the primary vehicle
    print("\n--- Fetching Vehicle List ---")
    vehicles_data = get_vehicles(token)
    first_vehicle_id = None
    if vehicles_data and 'response' in vehicles_data and vehicles_data['response']:
    
	    first_vehicle_id = vehicles_data['response'][0]['id']
	    # print(f"Found primary vehicle ID: {first_vehicle_id}")
#        print("Full vehicle list response:")
#        print(json.dumps(vehicles_data, indent=2))
    else:
	    print("No vehicles found in your Tesla account or unable to retrieve list.")
        
	# Proceed with data fetch and commands only if a vehicle ID was successfully found
    if first_vehicle_id:
	# 3. Fetch Detailed Vehicle Data (with automatic wake-up for 408 errors)
        # print(f"\n--- Attempting to Fetch Detailed Data for Vehicle {first_vehicle_id} ---")
        detailed_data = get_vehicle_data(token, first_vehicle_id, max_retries=5, initial_delay=8)
	
        if detailed_data and 'response' in detailed_data:
            print(f"Detailed vehicle data found for {first_vehicle_id}:")
#		print(json.dumps(detailed_data, indent=2))
        else:
            print(f"Could not retrieve detailed vehicle data for {first_vehicle_id} after retries.")
	
        json_output = {"tesla_status": {"battery_level": detailed_data["response"]["charge_state"]["battery_level"], "charge_state": detailed_data["response"]["charge_state"]["charging_state"], "battery_range": detailed_data["response"]["charge_state"]["battery_range"]  }}
	
        with open(output_filename, "w") as json_file:
            json.dump(json_output, json_file, indent=4)


# --- Main execution block ---
if __name__ == "__main__":
    # 0. Initial Setup Check
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: TESLA_CLIENT_ID and TESLA_CLIENT_SECRET must be set in your .env file.")
        print("Please create a .env file with these variables and TESLA_INITIAL_REFRESH_TOKEN (after first manual auth).")
        exit(1)

    # 1. Get a valid access token (will refresh if needed, or use initial from .env)
    token = get_valid_access_token()

    if not token:
        print("Failed to get a valid access token. Cannot proceed with API calls.")
        exit(1)

    # 2. List vehicles to get the ID of the primary vehicle
    print("\n--- Fetching Vehicle List ---")
    vehicles_data = get_vehicles(token)
    first_vehicle_id = None
    if vehicles_data and 'response' in vehicles_data and vehicles_data['response']:
        first_vehicle_id = vehicles_data['response'][0]['id']
        print(f"Found primary vehicle ID: {first_vehicle_id}")
        print("Full vehicle list response:")
        print(json.dumps(vehicles_data, indent=2))
    else:
        print("No vehicles found in your Tesla account or unable to retrieve list.")
    
    # Proceed with data fetch and commands only if a vehicle ID was successfully found
    if first_vehicle_id:
        # 3. Fetch Detailed Vehicle Data (with automatic wake-up for 408 errors)
        print(f"\n--- Attempting to Fetch Detailed Data for Vehicle {first_vehicle_id} ---")
        # Adjust max_retries and initial_delay as per your preference
        detailed_data = get_vehicle_data(token, first_vehicle_id, max_retries=5, initial_delay=8)
        
        if detailed_data and 'response' in detailed_data:
            print(f"Detailed vehicle data for {first_vehicle_id}:")
            print(json.dumps(detailed_data, indent=2))
            
            # Example: Extract and print latitude and longitude if available
            if 'drive_state' in detailed_data['response']:
                lat = detailed_data['response']['drive_state'].get('latitude')
                lon = detailed_data['response']['drive_state'].get('longitude')
                print(f"\nVehicle Location: Latitude={lat}, Longitude={lon}")
            else:
                print("Drive state data not available in detailed response.")
        else:
            print(f"Could not retrieve detailed vehicle data for {first_vehicle_id} after retries.")
        print("LLM Prompt: {}% battery remaining. Charge State: {}. Estimated range: {} miles.".format(detailed_data["response"]["charge_state"]["battery_level"],detailed_data["response"]["charge_state"]["charging_state"],detailed_data["response"]["charge_state"]["battery_range"]))
    
        json_output = {"tesla_status": {"battery_level": detailed_data["response"]["charge_state"]["battery_level"], "charge_state": detailed_data["response"]["charge_state"]["charging_state"], "battery_range": detailed_data["response"]["charge_state"]["battery_range"]  }}
		
        with open(output_filename, "w") as json_file:
            json.dump(json_output, json_file, indent=4)
			
    print("\n--- Script execution finished ---")
