import requests

url = "https://rp0kq2egtk.execute-api.ap-southeast-2.amazonaws.com/control/stop"
headers = {
    'auth': 'APIAUTH'
}

response = requests.request("POST", url, headers=headers)

print(response.text)
 