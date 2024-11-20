import http.client
import json
from datetime import datetime

# Function to read the stored refresh token from a file
def read_refresh_token():
    try:
        with open("refresh_token.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("No refresh token file found.")
        return None

# Function to save the new refresh token to a file
def save_refresh_token(token):
    with open("refresh_token.txt", "w") as file:
        file.write(token)

def generate_access_token():
    # Read the refresh token from file (or replace this with your initial token if running for the first time)
    refresh_token = read_refresh_token()
    if not refresh_token:
        # Use the initial token here if no file exists
        refresh_token = "eyJhbGciOiJSUzI1NiJ9.eyJhcHBfdHlwZSI6InN5c3RlbSIsInVzZXJfbmFtZSI6ImNhbXB1c2Zhcm1AdW1pY2guZWR1IiwiZW5sX2NpZCI6IiIsImVubF9wYXNzd29yZF9sYXN0X2NoYW5nZWQiOiIxNzI3MTkxNjkyIiwiYXV0aG9yaXRpZXMiOlsiUk9MRV9VU0VSIl0sImNsaWVudF9pZCI6IjNiNTRlZTExYTMwMzdhZDQzMmFmODhiM2NkYTJkOWRjIiwiYXVkIjpbIm9hdXRoMi1yZXNvdXJjZSJdLCJpc19pbnRlcm5hbF9hcHAiOmZhbHNlLCJzY29wZSI6WyJyZWFkIiwid3JpdGUiXSwiYXRpIjoiZDI1NGVlZmItOTM0OS00ODU4LWIxMmYtZWJjZWNlNTU0OThmIiwiZXhwIjoxNzMzNTgzMTcyLCJlbmxfdWlkIjoiNDgxNTIxMSIsImFwcF9JZCI6IjE0MDk2MjQ5ODk1OTUiLCJqdGkiOiI5MWYwZjNjNy1jMTgzLTRhZjItYWNmNS1mMzA4YTc2OGYwNGUifQ.VMPz6oWbvSPXc4GtKydOmoM5TuQSuf3JJrUEPs_Io7o6CQi_s0_36Pn5Bj-CKog3__ie9ckAsrsA8_scNOr6_l-iOs0w7I8HNHHbqe4xPco_CjdRIXTJjYPmY0-LRHKnrqkgCxOS1UXk9wdiTqxjw7TMj7dt8DslGvWL-2IaS3w"

    # Set up the connection and headers
    conn = http.client.HTTPSConnection("api.enphaseenergy.com")
    payload = ''
    headers = {
        'Authorization': 'Basic M2I1NGVlMTFhMzAzN2FkNDMyYWY4OGIzY2RhMmQ5ZGM6ODhmNTk2NWZmNGM3MzYxYzFlYjg3OTkzODZiMzY0MzM='
    }

    # Make the request with the current refresh token
    conn.request("POST", f"/oauth/token?grant_type=refresh_token&refresh_token={refresh_token}", payload, headers)
    res = conn.getresponse()
    data = res.read()

    # Decode and parse the JSON response
    response = json.loads(data.decode("utf-8"))

    # Check if the request was successful and save the new refresh token
    if 'refresh_token' in response:
        new_refresh_token = response['refresh_token']
        save_refresh_token(new_refresh_token)
        print("New refresh token saved.")
    else:
        print("Failed to obtain refresh token:", response)

    # Print the access token or other relevant information
    if 'access_token' in response:
        return response['access_token']
        #print("Access token:", response['access_token'])
    else:
        print("Failed to obtain access token:", response)



auth = generate_access_token()


conn = http.client.HTTPSConnection("api.enphaseenergy.com")
payload = ''
headers = {
    'Authorization': f"bearer {auth}",
    'key': 'd1128633c6e5948cd2c26be1c668900b'
}

conn.request("GET", "/api/v4/systems/5458246/ev_charger/202432007375/sessions", payload, headers)
res = conn.getresponse()
data = res.read()

# Parse the JSON response
response_data = json.loads(data.decode("utf-8"))

# Access the sessions
sessions = response_data.get("sessions", [])

# Iterate through each session and print details with human-readable times
for i, session in enumerate(sessions, start=1):
    start_time_human = datetime.fromtimestamp(session['start_time']).strftime('%Y-%m-%d %H:%M:%S')
    end_time_human = datetime.fromtimestamp(session['end_time']).strftime('%Y-%m-%d %H:%M:%S')
    
    # print(f"Session {i}:")
    # print(f"  Start Time: {start_time_human}")
    # print(f"  End Time: {end_time_human}")
    # print(f"  Duration: {session['duration']} seconds")
    # print(f"  Energy Added: {session['energy_added']} kWh")
    # print(f"  Charge Time: {session['charge_time']} seconds")
    # print(f"  Miles Added: {session['miles_added']}")
    # print(f"  Cost: {session['cost']}")
    # print()

def get_miles_added():
    return sessions[0]['miles_added']
