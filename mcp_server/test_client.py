import requests
import json

url = "http://127.0.0.1:5001/api"

data = {
    "method": "delete_caption",
    "params": {
        "id": "17627822628632863798"
    }
}

headers = {'Content-Type': 'application/json'}

response = requests.post(url, data=json.dumps(data), headers=headers)

print(response.json())