import requests
import matplotlib.pyplot as plt
import numpy as np

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
    print(rsp.text)

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
    params = {
        "region": "CAISO_NORTH",
        "signal_type": "co2_moer",
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

token = get_login_token()
# # print(token)
data = get_moer(token)
# print(data)
time = []
value = []
t = 0
for entry in data['data']:
    time.append(5*t)
    # print(f"Point Time: {data['point_time']}, Value: {data['value']}")
    # print(f"Point Time: {entry['point_time']}, Value: {entry['value']}")
    military_time = entry['point_time'].split('T')[1].split('+')[0]
    hours = int(military_time[0:2])
    mins = int(military_time[3:5])
    value.append(entry['value'])
    t+=1

value_array = np.array(value)
time_block_list = []
# print(value)
# 30 min blocks, 48 blocks, pick 16 blocks
for i in range(48):
    temp = value_array[6*i:6*(i+1)]
    ave = np.mean(temp)
    time_block_list.append(ave)

# print((time_block_list)) # contain MOER ave values
x = time_block_list
x = np.sort(x)
result = np.argpartition(time_block_list, 16)[:16]
result = np.sort(result)
# print(result)
# print(x[15])

extracted_time = []
for el in result:
    time_block = (el * 30, (el+1) * 30)
    extracted_time.append(time_block)
print("Extracted clean periods are:", extracted_time)

# plt.figure()
# plt.plot(time, value) 
# for start, end in extracted_time:
#     plt.fill_between(time, value, where=(time >= start) & (time <= end), color='green', alpha=0.5)
# plt.xlabel('Time/min')  
# plt.ylabel('MOER (lbs CO_2/MWh)') 
# plt.title('Marginal Operating Emission Rate - Region CAISO_NORTH')
# plt.savefig("watttime.png")

def get_clean_periods():
    return extracted_time, x[15]
print(x[15])
