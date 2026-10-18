
import requests


url = "https://molina-ac4-1.onrender.com/campus"

try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    # Retrieve JSON response
    data = response.json()

    print("CAMPUS API RESPONSE")
    print("-------------------")
    print("Campus:", data["campus"])
    print("Location:", data["location"])
    print("Status:", data["status"])
    print("Type:", data["type"])

except requests.exceptions.RequestException as error:
    print("Request error:", error)
except (ValueError, KeyError) as error:
    print("Response error:", error)
