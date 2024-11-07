import http.client
import json
import time

def read_refresh_token():
    try:
        with open("refresh_token.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("No refresh token file found.")
        return None

def save_refresh_token(token):
    with open("refresh_token.txt", "w") as file:
        file.write(token)

def get_access_token():
    refresh_token = read_refresh_token()
    if not refresh_token:
        refresh_token = "eyJhbGciOiJSUzI1NiJ9.eyJhcHBfdHlwZSI6InN5c3RlbSIsInVzZXJfbmFtZSI6ImNhbXB1c2Zhcm1AdW1pY2guZWR1IiwiZW5sX2NpZCI6IiIsImVubF9wYXNzd29yZF9sYXN0X2NoYW5nZWQiOiIxNzI3MTkxNjkyIiwiYXV0aG9yaXRpZXMiOlsiUk9MRV9VU0VSIl0sImNsaWVudF9pZCI6IjNiNTRlZTExYTMwMzdhZDQzMmFmODhiM2NkYTJkOWRjIiwiYXVkIjpbIm9hdXRoMi1yZXNvdXJjZSJdLCJpc19pbnRlcm5hbF9hcHAiOmZhbHNlLCJzY29wZSI6WyJyZWFkIiwid3JpdGUiXSwiYXRpIjoiZDI1NGVlZmItOTM0OS00ODU4LWIxMmYtZWJjZWNlNTU0OThmIiwiZXhwIjoxNzMzNTgzMTcyLCJlbmxfdWlkIjoiNDgxNTIxMSIsImFwcF9JZCI6IjE0MDk2MjQ5ODk1OTUiLCJqdGkiOiI5MWYwZjNjNy1jMTgzLTRhZjItYWNmNS1mMzA4YTc2OGYwNGUifQ.VMPz6oWbvSPXc4GtKydOmoM5TuQSuf3JJrUEPs_Io7o6CQi_s0_36Pn5Bj-CKog3__ie9ckAsrsA8_scNOr6_l-iOs0w7I8HNHHbqe4xPco_CjdRIXTJjYPmY0-LRHKnrqkgCxOS1UXk9wdiTqxjw7TMj7dt8DslGvWL-2IaS3w"

    payload = ''
    headers = {
        'Authorization': 'Basic M2I1NGVlMTFhMzAzN2FkNDMyYWY4OGIzY2RhMmQ5ZGM6ODhmNTk2NWZmNGM3MzYxYzFlYjg3OTkzODZiMzY0MzM='
    }
    
    for attempt in range(5):  # Retry up to 5 times
        conn = http.client.HTTPSConnection("api.enphaseenergy.com")  # New connection each attempt
        conn.request("POST", f"/oauth/token?grant_type=refresh_token&refresh_token={refresh_token}", payload, headers)
        
        try:
            res = conn.getresponse()
            
            if res.status == 200:
                data = res.read()
                try:
                    response = json.loads(data.decode("utf-8"))
                    
                    if 'refresh_token' in response:
                        save_refresh_token(response['refresh_token'])
                        print("New refresh token saved.")

                    if 'access_token' in response:
                        print("Access token:", response['access_token'])
                    else:
                        print("Failed to obtain access token:", response)
                    return  # Exit after successful request
                except json.JSONDecodeError:
                    print("Error: Unable to parse JSON response. Response was:", data.decode("utf-8"))
                    return
            else:
                print(f"Attempt {attempt + 1}: Error {res.status} - {res.reason}")
                time.sleep(2 ** attempt)  # Exponential backoff: 1, 2, 4, 8, 16 seconds

        except http.client.ResponseNotReady:
            print("ResponseNotReady error encountered. Retrying...")
            time.sleep(2 ** attempt)

        finally:
            conn.close()  # Ensure connection is closed after each attempt

    print("All retry attempts failed. Please try again later.")

get_access_token()
