import requests
import json

# Define the URL for the GET request
url = "https://api.currencylayer.com/live?access_key=197e2e66ec1ac07d69c0e578330cc527"
# querystring = {"base": "USD"}

# Make the GET request
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    
    # Save the data to a JSON file
    with open("C:\\Users\\kapse\\Desktop\\Pythonproject\\Archive\\Binance\\exchange_rates\\exchange_rates.json", "w") as json_file:
        json.dump(data, json_file, indent=4)
    
    print("Data has been saved to exchange_rates.json")
else:
    print(f"Request failed with status code {response.status_code}")
