import requests

CLASSMATE_BASE_URL = "https://palencia-shamainejoyce.onrender.com"
ENDPOINT = "/courses"

url = f"{CLASSMATE_BASE_URL}{ENDPOINT}"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("--- Classmate's API Response ---")
    if isinstance(data, dict):
        for key, value in data.items():
            print(f"{key.capitalize()}: {value}")
    else:
        print("Data:", data)
else:
    print("Request failed.")
    print("Status Code:", response.status_code)