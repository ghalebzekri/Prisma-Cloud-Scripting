import os
import json
import csv
import requests
from bs4 import BeautifulSoup

# Define the URL of the repository
repo_url = "https://github.com/PaloAltoNetworks/prisma-cloud-policies/tree/master/policies"

# Directory to save JSON files locally
json_dir = "policies"

# Output CSV file
output_csv = "prisma_cloud_policies.csv"

# Function to download JSON files from GitHub if needed
def download_json_files():
    response = requests.get(repo_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all JSON file links in the repository
    json_files = []
    for link in soup.find_all('a', href=True):
        if link['href'].endswith('.json'):
            json_files.append("https://raw.githubusercontent.com" + link['href'].replace('/blob', ''))

    # Ensure JSON directory exists
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)

    # Download each JSON file into the policies directory
    for json_file_url in json_files:
        file_name = os.path.join(json_dir, os.path.basename(json_file_url))
        if not os.path.exists(file_name):  # Skip if file already exists
            with requests.get(json_file_url) as response:
                if response.status_code == 200:
                    with open(file_name, 'w') as file:
                        file.write(response.text)

# Call the function to download JSON files
download_json_files()

# Open the CSV file for writing
with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ["policyUpi", "policyId", "policyType", "cloudType", "severity", "name", "description", "searchModel.query"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    # Loop through each JSON file in the policies directory
    for file_name in os.listdir(json_dir):
        if file_name.endswith(".json"):
            file_path = os.path.join(json_dir, file_name)
            
            # Open and parse the JSON file
            with open(file_path, 'r', encoding='utf-8') as json_file:
                try:
                    data = json.load(json_file)
                    
                    # Extract only the specified fields
                    extracted_data = {
                        "policyUpi": data.get("policyUpi", "Missing"),
                        "policyId": data.get("policyId", "Missing"),
                        "policyType": data.get("policyType", "Missing"),
                        "cloudType": data.get("cloudType", "Missing"),
                        "severity": data.get("severity", "Missing"),
                        "name": data.get("name", "Missing"),
                        "description": data.get("description", "Missing").replace("\n", " "),
                        "searchModel.query": data.get("searchModel.query", "Missing"),
                    }
                    
                    # Write the extracted data to the CSV file
                    writer.writerow(extracted_data)
                
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from file {file_name}: {e}")

print(f"Data has been successfully extracted to {output_csv}")