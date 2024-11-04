import http.client
import json

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

# Read the refresh token from file (or replace this with your initial token if running for the first time)
refresh_token = read_refresh_token()
if not refresh_token:
    # Use the initial token here if no file exists
    refresh_token = "eyJhbGciOiJSUzI1NiJ9.eyJhcHBfdHlwZSI6InN5c3RlbSIsInVzZXJfbmFtZSI6ImNhbXB1c2Zhcm1AdW1pY2guZWR1IiwiZW5sX2NpZCI6IiIsImVubF9wYXNzd29yZF9sYXN0X2NoYW5nZWQiOiIxNzI3MTkxNjkyIiwiYXV0aG9yaXRpZXMiOlsiUk9MRV9VU0VSIl0sImNsaWVudF9pZCI6IjNiNTRlZTExYTMwMzdhZDQzMmFmODhiM2NkYTJkOWRjIiwiYXVkIjpbIm9hdXRoMi1yZXNvdXJjZSJdLCJpc19pbnRlcm5hbF9hcHAiOmZhbHNlLCJzY29wZSI6WyJyZWFkIiwid3JpdGUiXSwiYXRpIjoiZWUyMDQ5ZmMtZmMwYS00ODRhLThjOTctN2E5MTU2MzU3M2MwIiwiZXhwIjoxNzMzMzg4NDI1LCJlbmxfdWlkIjoiNDgxNTIxMSIsImFwcF9JZCI6IjE0MDk2MjQ5ODk1OTUiLCJqdGkiOiI0M2JlZGUzNi0wOTJiLTQ1YzktYjg0Zi05NzNjMjllMzA2ZDcifQ.K3DwLWP-lNlzDybGs1jKk5RQVTPujkHGsS1VA5v6JBRzwRNgjFIBPiBil1oYGZhplB-ZW5pVGL2GlEUbCbL0DXF_ue8SyOYVjZmMKQcTMkayZ0ER0yKyi1E1DlOJhV7XKdCiIVYYFeTZxIeF0wiuGmkJe0CSPvRw8tGSMHIx8bM"

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
    print("Access token:", response['access_token'])
else:
    print("Failed to obtain access token:", response)
