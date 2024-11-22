import requests
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from closestDelivery import get_next_delivery, read_schedule_from_csv
# from real_time_ems import get_amount_of_clean_periods
# import test as test
import csv
import pytz
import json 
import math

TIMEZONE = pytz.UTC
DETROIT_TIMEZONE = pytz.timezone("America/Detroit")
filepath = 'weeklySchedule.csv'
min_time_difference = None
hours_difference = 0
dirty_periods = []


real_time = datetime.now()

def perform_action_based_on_next_delivery():
    global min_time_difference
    global hours_difference

    schedule = read_schedule_from_csv(filepath)
    current_time = datetime.now(DETROIT_TIMEZONE)
    # Find the next delivery
    next_delivery, next_delivery_time, min_time_difference = get_next_delivery(schedule, current_time)
    print(next_delivery)
    print(next_delivery_time)
    hours_difference = min_time_difference.total_seconds() / 3600  # Convert to hours
    hours_difference = math.floor(hours_difference)  # Get the floored value

perform_action_based_on_next_delivery()

def get_current_time():
    print(real_time)
    return real_time

def make_account():
    
    # To register, use the code below. Please note that for these code examples we are using filler values for username
    # (freddo), password (the_frog), email (freddo@frog.org), org (freds world) and you should replace each if you are
    # copying and pasting this code.

    import requests
    register_url = 'https://api.watttime.org/register'
    params = {'username': 'nelfigs',
            'password': '%Trpriprq38$*nF',
            'email': 'nelfigs@umich.edu',
            'org': 'University of Michigan'}
    rsp = requests.post(register_url, json=params)
    # print(rsp.text)

def get_login_token():
    
    # To login and obtain an access token, use this code:
    import requests
    from requests.auth import HTTPBasicAuth
    login_url = 'https://api.watttime.org/login'
    rsp = requests.get(login_url, auth=HTTPBasicAuth('nelfigs', '%Trpriprq38$*nF'))
    TOKEN = rsp.json()['token']
    print(rsp.json())
    return TOKEN


def get_moer(token):
    url = "https://api.watttime.org/v3/forecast"

    # Provide your TOKEN here, see https://docs.watttime.org/#tag/Authentication/operation/get_token_login_get for more information
    TOKEN = ""
    headers = {"Authorization": f"Bearer {token}"}
    # Get the current time in Detroit's timezone
    current_time_detroit = datetime.now(DETROIT_TIMEZONE)
    # Convert Detroit time to UTC for the WattTime API
    # Forecast should start now (in Detroit time) and extend 24 hours
    start_time = current_time_detroit.isoformat()  # Detroit local time (ISO format)
    # end_time = (current_time_detroit + timedelta(hours=24)).isoformat()
    
    
    # Convert to UTC for WattTime API
    start_time_utc = current_time_detroit.astimezone(pytz.timezone("America/New_York")).isoformat()
    global min_time_difference
    global hours_difference
    print(hours_difference)
    print(min_time_difference)

    params = {
        "region": "MISO_DETROIT",
        "signal_type": "co2_moer"
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

token = get_login_token()
# print(token)
pre_data = get_moer(token)

data = []
for entry in pre_data['data']:
    original_time = datetime.fromisoformat(entry['point_time'])  # Parse the point_time
    adjusted_time = original_time - timedelta(hours=5)  # Subtract 5 hours
    data.append({
        "point_time": adjusted_time.isoformat(),
        "value": entry['value']
    })

print(data)

def generate_dirty_periods(num_time_slots_wanted):
    global data
    global TIMEZONE
    global dirty_periods
        
    # Extract values and times
    values = [entry['value'] for entry in data]
    times = [datetime.fromisoformat(entry['point_time']).astimezone(TIMEZONE) for entry in data]

    # Extract and sort 5-minute periods
    time_slots = [(value, times[i]) for i, value in enumerate(values)]  # Pair values with their timestamps

  # Sort by MOER value (descending)
    time_slots.sort(key=lambda x: x[0], reverse=True)  # Sort by the MOER value (highest first).

    # Select up to X hours worth of 5-minute periods (X*12 periods)
   # num_time_slots_wanted = get_amount_of_clean_periods()
    print(num_time_slots_wanted)
    selected_slots = time_slots[:num_time_slots_wanted]  # Take the first 84 slots (X hours)
    # Extract clean periods with full ISO 8601 timestamps
    dirty_periods = [(slot[1].isoformat(), (slot[1] + timedelta(minutes=5)).isoformat()) for slot in selected_slots]
    print(len(selected_slots))

def plot_dirty_periods(dirty_periods, values, times):
    """
    Visualize clean periods on a time-value plot.
    - Clean periods: Green
    - Other periods: Black
    """
    plt.figure(figsize=(12, 6))

    # Plot the entire dataset in blue
    plt.plot(times, values, color="blue", label="MOER Values")

    # Highlight clean periods in green
    for start, end in dirty_periods:
        # Convert clean period times (HH:MM) into datetime objects
# Parse full ISO 8601 timestamps for start and end
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

    # Customize plot
    plt.xlabel("Time")
    plt.ylabel("MOER (lbs CO₂/MWh)")
    plt.title(f"Dirty Time Periods - Region: Detroit")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(rotation=45)
    plt.legend(loc="upper right")

    # Save and show the plot
    plt.savefig("drity_periods.png")
    plt.show()


# plot_clean_periods(clean_periods,values,times)
# Save clean periods to a JSON file
def save_dirty_periods(filename="cooler_dirty_periods.json"):
    global dirty_periods
    with open(filename, "w") as file:
        json.dump(dirty_periods, file)
    print(f"dirty periods saved to {filename}")

generate_dirty_periods(36) # dirty periods (3 hours total)
# # # Save the clean periods
save_dirty_periods()
# print(datetime.now())


