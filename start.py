import os
import requests

url = "https://rp0kq2egtk.execute-api.ap-southeast-2.amazonaws.com/control/start"
headers = {
    'auth': os.environ['APIAUTH']
}

response = requests.request("POST", url, headers=headers)

print(response.text)