import requests
import base64
from ..runtimedata import account_pool
from time import time

def ringcentral_get_token(client_id, client_secret, jwt):
    auth_url = 'https://platform.ringcentral.com/restapi/oauth/token'
    auth_str = f"{client_id}:{client_secret}"
    auth_bytes = auth_str.encode('utf-8')
    auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')

    data = {}
    if not account_pool['ringcentral']:
        data['grant_type'] = 'urn:ietf:params:oauth:grant-type:jwt-bearer'
        data['assertion'] = jwt
    elif account_pool['ringcentral'].get('expires_in', 0) > time():
        return account_pool['ringcentral']['access_token']
    else:
        data['grant_type'] = 'refresh_token'
        data['client_id'] = client_id
        data['refresh_token'] = account_pool[0].get('refresh_token')

    headers = {}
    headers['Accept'] = 'application/json'
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    headers['Authorization'] = f'Basic {auth_b64}'

    resp = requests.post(auth_url, headers=headers, data=data).json()

    account_pool['ringcentral']['expires_in'] = resp.get('expires_in') + time()
    account_pool['ringcentral']['access_token'] = resp.get('access_token')
    account_pool['ringcentral']['refresh_token'] = resp.get('refresh_token')

    print(account_pool)
    return resp.get('access_token')


def ringcentral_send_sms(tophonenumber, fromphonenumber, text, token=None):
    if token:
        url = 'https://api-ucc.ringcentral.com/restapi/v1.0/account/~/extension/~/sms'
    else:
        token = ringcentral_get_token(self.input_ringcentral_client_id.text(), self.input_ringcentral_client_secret.text(), self.input_ringcentral_jwt.text())
        url = 'https://platform.ringcentral.com/restapi/v1.0/account/~/extension/~/sms'

    headers = {}
    headers['accept'] = 'application/json, text/plain, */*'
    headers['accept-language'] = 'en-US,en;q=0.9'
    headers['authorization'] = f'Bearer {token}'
    headers['cache-control'] = 'no-cache'
    headers['content-type'] = 'application/json'
    headers['origin'] = 'https://app.businessconnect.telus.com'
    headers['pragma'] = 'no-cache'
    headers['priority'] = 'u=1, i'
    headers['referer'] = 'https://app.businessconnect.telus.com/'
    headers['sec-ch-ua'] = '"Not)A;Brand";v="8", "Chromium";v="138"'
    headers['sec-ch-ua-mobile'] = '?0'
    headers['sec-ch-ua-platform'] = '"Linux"'
    headers['sec-fetch-dest'] = 'empty'
    headers['sec-fetch-mode'] = 'cors'
    headers['sec-fetch-site'] = 'cross-site'
    headers['user-agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
    headers['x-user-agent'] = 'BusinessConnectWeb/25.2.20 (BusinessConnect; Linux/x86_64; build.3599; rev.c8fba4c5d)'

    data = {
        "from": {"phoneNumber": f"+1{fromphonenumber}"},
        "to": [{"phoneNumber": f"+1{tophonenumber}"}],
        "text": f"{text}"
    }
    response = requests.post(url, headers=headers, json=data)
    print(response.status_code)
    print(response.json())

    if response.status_code != 200:
        raise Exception(response.json())
    return response.json()
