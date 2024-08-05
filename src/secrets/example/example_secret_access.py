from secrets_vault import SecretsVault
import json

# This example read the data from the secret vault (this presuppone that the environment variable contain already some data in it) and try to get the API kys relative
# to some services. You can also dump the entire json structure, once u have access to the crypto credentials.
# Note that the crypto credentials (salt file and psw file) are automatically loaded from the default location ~/.secrets_manager when the SecretsVault class is 
# istantiated. If not present, they will be created and used as the new crypto credentials.

def main():
    manager = SecretsVault.get_instance()
    
    # Get a specific secret
    api_key = manager.get_secret('google_maps', 'api_key')
    print(f"Google Maps API Key: {api_key}")
    
    # Get all secrets for a service
    github_secrets = manager.get_all_secrets_for_service('github')
    print("GitHub secrets:")
    print(json.dumps(github_secrets, indent=2))
    
    # Get all available services
    services = manager.get_all_services()
    print("Available services:")
    print(json.dumps(services, indent=2))

if __name__ == "__main__":
    main()