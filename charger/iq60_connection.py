import http.client



conn = http.client.HTTPSConnection("api.enphaseenergy.com")
payload = ''
headers = {
  'Authorization': '355f50fbae2cfdd2defa56de369d5d6c'
  #if the auth code doesn't work, try this --> fcc3b392452b9b845a3a4cba80eece16
}
conn.request("GET", "/api/v4/systems?key=fcc3b392452b9b845a3a4cba80eece16", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))