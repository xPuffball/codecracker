import requests
import json

base_url = "https://159.203.7.203/generate-hints"

# Data to be sent in the request
data = {
    "my_words": [
        "tennis",
        "pepper",
        "kind",
        "home",
        "head",
        "team",
        "problem",
        "lot",
        "business"
    ],
    "opponent_words": [
        "world",
        "interest",
        "elephant",
        "family",
        "car",
        "sand",
        "monkey",
        "snow",
    ],
    "neutral_words": [
        "elephant",
        "family",
        "car",
        "question",
        "beach",
        "art",
        "port"
    ],
    "assassin_word": "monkey"
}
# Send POST request with JSON data
response = requests.post(base_url, json=data, verify=False)

# Check the response
if response.status_code == 200:
    print("Request successful!")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
else:
    print(f"Request failed with status code: {response.status_code}")
    print("Response:")
    print(response.text)

    