import requests
import json

base_url = "http://127.0.0.1:5000/generate-hints"

# Data to be sent in the request
data = {
    "my_words": ["apple", "tree", "green"],
    "opponent_words": ["car", "road", "wheel"],
    "neutral_words": ["house", "window", "door"],
    "assassin_word": "poison"
}

# Send POST request with JSON data
response = requests.post(base_url, json=data)

# Check the response
if response.status_code == 200:
    print("Request successful!")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
else:
    print(f"Request failed with status code: {response.status_code}")
    print("Response:")
    print(response.text)