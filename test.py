import json
import requests
from test1 import data

url = 'http://127.0.0.1:8000/api-token-auth/'
r = requests.post(url, data=data)

token = json.loads(r.text)['token']

print('Token is : ', token)

url = 'http://127.0.0.1:8000/hello/'
headers = {'Authorization': 'Token {}'.format(token)}
r = requests.get(url, headers=headers)

print('Response is : ', r.text)
