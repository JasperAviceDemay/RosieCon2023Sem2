import os
import requests
import time

url = "https://rp0kq2egtk.execute-api.ap-southeast-2.amazonaws.com/control/stop"
headers = {
    'auth': os.environ['APIAUTH']
}

time.sleep(30)

response = requests.request("POST", url, headers=headers)

print(response.text)
 
