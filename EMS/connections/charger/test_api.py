import http.client

conn = http.client.HTTPSConnection("api.enphaseenergy.com")
payload = ''
headers = {
    'Authorization': 'bearer eyJhbGciOiJSUzI1NiJ9.eyJhcHBfdHlwZSI6InN5c3RlbSIsInVzZXJfbmFtZSI6ImNhbXB1c2Zhcm1AdW1pY2guZWR1IiwiZW5sX2NpZCI6IiIsImVubF9wYXNzd29yZF9sYXN0X2NoYW5nZWQiOiIxNzI3MTkxNjkyIiwiYXV0aG9yaXRpZXMiOlsiUk9MRV9VU0VSIl0sImNsaWVudF9pZCI6IjNiNTRlZTExYTMwMzdhZDQzMmFmODhiM2NkYTJkOWRjIiwiYXVkIjpbIm9hdXRoMi1yZXNvdXJjZSJdLCJpc19pbnRlcm5hbF9hcHAiOmZhbHNlLCJzY29wZSI6WyJyZWFkIiwid3JpdGUiXSwiZXhwIjoxNzI4NzczMTY5LCJlbmxfdWlkIjoiNDgxNTIxMSIsImFwcF9JZCI6IjE0MDk2MjQ5ODk1OTUiLCJqdGkiOiI5NjMzMmZjMi1kMTdmLTQ1NGEtODY4Yy01ZjA2YmRiZWRkZGYifQ.Rr77dZAn1hjzcCnosncj4xwZrU9W_Xmvo5IuzdrMUkykiwKJHx82sLILqK0M5oZhxcmEfa9V3Md1vkOa6theGKc2FUUgn0g2uTvlJc4BMdKS14DPRUrOrBsTCVyTsmUNFttVZIZ-R4oTs30RRii2jpE9UH-V7MmcArpk-Si8s_Y',
    'key': 'd1128633c6e5948cd2c26be1c668900b',
    'system_id': '5458246',  # Example system_id
    'serial_no': '202432007375'
}

# Extract the system_id from the headers
system_id = headers['system_id']
serial_no = headers['serial_no']

# Construct the API endpoint using the extracted system_id
endpoint = f"/api/v4/systems/{system_id}/ev_charger/{serial_no}/stop_charging"

conn.request("POST", endpoint, payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
