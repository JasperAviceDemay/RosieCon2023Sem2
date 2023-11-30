import os
import requests
import time

url = "https://rp0kq2egtk.execute-api.ap-southeast-2.amazonaws.com/control/start"
headers = {
    'auth': os.environ['APIAUTH']
}


response = requests.request
(while True:
    try:
        response = requests.request("POST", url, headers=headers)
        if response.status_code >= 200 and response.status_code < 300:
            print(response.text)
            break
        else:
            print(f"Request failed with status {response.status_code}, retrying...")
            time.sleep(20)  # wait for 5 seconds before retrying
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}, retrying...")
        time.sleep(20)  "POST", url, headers=headers)

print(response.text)
