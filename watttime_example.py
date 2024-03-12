import requests


def make_account():
    
    # To register, use the code below. Please note that for these code examples we are using filler values for username
    # (freddo), password (the_frog), email (freddo@frog.org), org (freds world) and you should replace each if you are
    # copying and pasting this code.

    import requests
    register_url = 'https://api.watttime.org/register'
    params = {'username': 'sfay',
            'password': 'uY*B5#sxbcLgMa',
            'email': 'smafay6@gmail.com',
            'org': 'University of Michigan'}
    rsp = requests.post(register_url, json=params)
    print(rsp.text)

def get_login_token():
    
    # To login and obtain an access token, use this code:
    import requests
    from requests.auth import HTTPBasicAuth
    login_url = 'https://api.watttime.org/login'
    rsp = requests.get(login_url, auth=HTTPBasicAuth('sfay', 'uY*B5#sxbcLgMa'))
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
    print(response.json())

token = get_login_token()
print(token)
get_moer(token)