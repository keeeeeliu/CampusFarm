import http.client

conn = http.client.HTTPSConnection("api.enphaseenergy.com")
payload = ''
headers = {
    #insert access_token
  'Authorization': 'bearer eyJhbGciOiJSUzI1NiJ9.eyJhcHBfdHlwZSI6InN5c3RlbSIsInVzZXJfbmFtZSI6ImNhbXB1c2Zhcm1AdW1pY2guZWR1IiwiZW5sX2NpZCI6IiIsImVubF9wYXNzd29yZF9sYXN0X2NoYW5nZWQiOiIxNzI3MTkxNjkyIiwiYXV0aG9yaXRpZXMiOlsiUk9MRV9VU0VSIl0sImNsaWVudF9pZCI6IjNiNTRlZTExYTMwMzdhZDQzMmFmODhiM2NkYTJkOWRjIiwiYXVkIjpbIm9hdXRoMi1yZXNvdXJjZSJdLCJpc19pbnRlcm5hbF9hcHAiOmZhbHNlLCJzY29wZSI6WyJyZWFkIiwid3JpdGUiXSwiZXhwIjoxNzI5NjU2MDQyLCJlbmxfdWlkIjoiNDgxNTIxMSIsImFwcF9JZCI6IjE0MDk2MjQ5ODk1OTUiLCJqdGkiOiI0ZmJmNjQ2Ni1kMmM1LTQzY2UtYjQ3Yi1jY2NkY2MxODE3ZjEifQ.MKla1EY6uIOIv6O1mwun9lxXgR9hDxFs_n9XIY4FXd7enzZspCfYoF7y5p5byfWd4NvO3AJtiibga9Dd_Me4T8_668Pre10ZMf-nhDagAn9kqFcGdU6tU_4Ww8sBZz_wCguF33P37nCZYfqHDxOMa0sIJsLcpWEna0dmaqw1_iY',
  'key': 'd1128633c6e5948cd2c26be1c668900b'
}

conn.request("GET", "/api/v4/systems/5458246/live_data", payload, headers)
#ev_charger/202432007375/telemetry
#/5458246/ev_charger/devices
res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))