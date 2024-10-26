import os
import json
import csv
import requests

# URL du dépôt GitHub et répertoire des JSONs
repo_url = "https://api.github.com/repos/PaloAltoNetworks/prisma-cloud-policies/contents/policies"
json_dir = "policies"
output_csv = "prisma_cloud_policies_final.csv"

# Fonction pour télécharger les fichiers JSON depuis le répertoire 'policies' du dépôt
def download_json_files():
    headers = {"Accept": "application/vnd.github.v3+json"}
    response = requests.get(repo_url, headers=headers)
    
    if response.status_code == 200:
        json_files = response.json()
        
        # Créer le répertoire local s'il n'existe pas
        if not os.path.exists(json_dir):
            os.makedirs(json_dir)

        # Télécharger chaque fichier JSON dans le répertoire
        for file_info in json_files:
            if file_info['name'].endswith('.json'):
                json_url = file_info['download_url']
                file_name = os.path.join(json_dir, file_info['name'])
                
                if not os.path.exists(file_name):  # Éviter de télécharger les fichiers déjà présents
                    with requests.get(json_url) as response:
                        if response.status_code == 200:
                            with open(file_name, 'w') as file:
                                file.write(response.text)
    else:
        print("Erreur lors de la récupération des fichiers JSON :", response.status_code)

# Appeler la fonction pour télécharger les fichiers JSON
download_json_files()

# Ouvrir le fichier CSV pour écrire les données extraites
with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ["policyUpi", "policyId", "policyType", "cloudType", "severity", "name", "description", "searchModel.query"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    # Parcourir chaque fichier JSON dans le répertoire des policies
    for file_name in os.listdir(json_dir):
        if file_name.endswith(".json"):
            file_path = os.path.join(json_dir, file_name)
            
            # Ouvrir et analyser le fichier JSON
            with open(file_path, 'r', encoding='utf-8') as json_file:
                try:
                    data = json.load(json_file)
                    
                    # Extraire uniquement les champs spécifiés
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
                    
                    # Écrire les données extraites dans le fichier CSV
                    writer.writerow(extracted_data)
                
                except json.JSONDecodeError as e:
                    print(f"Erreur de décodage JSON dans le fichier {file_name} : {e}")

print(f"Les données ont été extraites avec succès dans {output_csv}")