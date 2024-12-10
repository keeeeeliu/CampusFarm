import http.client
import json
from datetime import datetime

conn = http.client.HTTPSConnection("api.enphaseenergy.com")
payload = ''
headers = {
    'Authorization': 'bearer eyJhbGciOiJSUzI1NiJ9.eyJhcHBfdHlwZSI6InN5c3RlbSIsInVzZXJfbmFtZSI6ImNhbXB1c2Zhcm1AdW1pY2guZWR1IiwiZW5sX2NpZCI6IiIsImVubF9wYXNzd29yZF9sYXN0X2NoYW5nZWQiOiIxNzI3MTkxNjkyIiwiYXV0aG9yaXRpZXMiOlsiUk9MRV9VU0VSIl0sImNsaWVudF9pZCI6IjNiNTRlZTExYTMwMzdhZDQzMmFmODhiM2NkYTJkOWRjIiwiYXVkIjpbIm9hdXRoMi1yZXNvdXJjZSJdLCJpc19pbnRlcm5hbF9hcHAiOmZhbHNlLCJzY29wZSI6WyJyZWFkIiwid3JpdGUiXSwiZXhwIjoxNzMxMDMzNzk4LCJlbmxfdWlkIjoiNDgxNTIxMSIsImFwcF9JZCI6IjE0MDk2MjQ5ODk1OTUiLCJqdGkiOiI0ZjlhYTg1Zi1jMDMwLTRmY2MtODU1ZS04OGM4NzBmMzA4ZjMifQ.Q-CNpzJMe7b0XNH8PkH-I58Sl2QRgUxrhPvtOAvHO8MoRcR1iKqsu_q_AGpB8F4PHMiAyhOgJqrbhjFa5F1QEsZV01obr0XfiOj87R4o3w_-walzFFU-bEZdo8nfWhI3XligATQ479mSCcshBm8WQHQDl_zizHcd5llXbXvFwC4',
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
    
    print(f"Session {i}:")
    print(f"  Start Time: {start_time_human}")
    print(f"  End Time: {end_time_human}")
    print(f"  Duration: {session['duration']} seconds")
    print(f"  Energy Added: {session['energy_added']} kWh")
    print(f"  Charge Time: {session['charge_time']} seconds")
    print(f"  Miles Added: {session['miles_added']}")
    print(f"  Cost: {session['cost']}")
    print()
