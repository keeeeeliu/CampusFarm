import http.client

conn = http.client.HTTPSConnection("api.enphaseenergy.com")
payload = ''
headers = {
  'Authorization': 'Bearer unique_access_token'
}
conn.request("GET", "/api/v4/systems?key=b2b2fd806ed13efb463691b436957798", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))