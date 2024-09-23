import requests
import json

base_url = "http://159.203.7.203:5000/generate-hints"

# Data to be sent in the request
data = {
    "my_words": ["apple", "tree", 'test', 'paper', 'gun', 'war', 'cup'],
    "opponent_words": ["car", "road", "wheel",'poop','pee','stupid','hello','greetings','laptop'],
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