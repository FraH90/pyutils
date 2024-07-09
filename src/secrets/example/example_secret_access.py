from secrets_vault import SecretsVault
import json

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