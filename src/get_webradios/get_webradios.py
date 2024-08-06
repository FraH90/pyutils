import requests
import json

# Define the URL for the Radio Browser API
url = "https://de1.api.radio-browser.info/json/stations/bycountry/Italy"

# Fetch the data
response = requests.get(url)
stations = response.json()

# Extract only the required fields
extracted_data = []
for station in stations:
    extracted_data.append({
        "name": station.get("name"),
        "url": station.get("url"),
        "url_resolved": station.get("url_resolved"),
        "homepage": station.get("homepage")
    })

# Define the output file path
output_file = "extracted_radio_stations.json"

# Write the extracted data to a file
with open(output_file, 'w') as file:
    json.dump(extracted_data, file, indent=4)

print(f"Extracted radio stations have been written to {output_file}")
