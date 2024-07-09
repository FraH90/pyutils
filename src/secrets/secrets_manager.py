import os
import json
from secrets_vault import SecretsVault
import datetime
import shutil

def merge_secrets(existing_secrets, new_secrets):
    for service, data in new_secrets.get('services', {}).items():
        if service in existing_secrets['services']:
            existing_secrets['services'][service].update(data)
        else:
            existing_secrets['services'][service] = data
    return existing_secrets

def write_secrets_from_json(vault):
    json_file_path = input("Enter the path to your JSON file containing secrets: ")
    
    if not os.path.exists(json_file_path):
        print(f"Error: File '{json_file_path}' not found.")
        return

    try:
        with open(json_file_path, 'r') as f:
            new_secrets = json.load(f)
        
        # Check if there are existing secrets
        vault.decrypt_and_load()
        if vault.secrets_data.get('services'):
            choice = input("Existing secrets found. Do you want to (A)ppend new data or (O)verwrite? [A/O]: ").lower()
            if choice == 'a':
                vault.secrets_data = merge_secrets(vault.secrets_data, new_secrets)
            elif choice == 'o':
                vault.secrets_data = new_secrets
            else:
                print("Invalid choice. Operation cancelled.")
                return
        else:
            vault.secrets_data = new_secrets
        
        # Encrypt and store updated secrets
        vault.encrypt_and_store(vault.secrets_data)
        print("Secrets have been successfully processed and stored in the environment variable.")
    except Exception as e:
        print(f"An error occurred: {e}")

def manually_enter_secrets(vault):
    # Check if there are existing secrets
    vault.decrypt_and_load()
    if vault.secrets_data.get('services'):
        choice = input("Existing secrets found. Do you want to (A)ppend new data or (O)verwrite? [A/O]: ").lower()
        if choice == 'o':
            vault.secrets_data = {'services': {}}
        elif choice != 'a':
            print("Invalid choice. Operation cancelled.")
            return
    else:
        vault.secrets_data = {'services': {}}
    
    while True:
        service_name = input("Enter service name (or 'x' to finish): ")
        if service_name.lower() == 'x':
            break
        
        service_data = {}
        fields = ['name', 'username', 'password', 'api_key', 'public_key', 'secret_key']
        
        for field in fields:
            value = input(f"Enter {field} (leave empty for None): ")
            service_data[field] = value if value else None
        
        # Ask for any additional fields
        while True:
            additional_field = input("Enter any additional field name (or press Enter to finish): ")
            if not additional_field:
                break
            value = input(f"Enter value for {additional_field}: ")
            service_data[additional_field] = value if value else None
        
        if service_name in vault.secrets_data['services']:
            vault.secrets_data['services'][service_name].update(service_data)
        else:
            vault.secrets_data['services'][service_name] = service_data
    
    # Encrypt and store updated secrets
    vault.encrypt_and_store(vault.secrets_data)
    print("Secrets have been successfully updated, encrypted, and stored in the environment variable.")


def backup_secrets(vault):
    try:
        # Create a backup directory
        backup_dir = f"secrets_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)

        # Export and save secrets
        secrets_json = vault.export_secrets()
        with open(os.path.join(backup_dir, 'secrets_backup.json'), 'w') as f:
            f.write(secrets_json)

        # Backup configuration files
        config_files = vault.get_saltpsw_path()
        for file_type, file_path in config_files.items():
            if os.path.exists(file_path):
                shutil.copy2(file_path, os.path.join(backup_dir, f'{file_type}.bin'))
            else:
                print(f"Warning: {file_type} file not found at {file_path}")

        print(f"Backup completed successfully. Backup directory: {backup_dir}")
    except Exception as e:
        print(f"An error occurred during backup: {e}")

def main():
    vault = SecretsVault.get_instance()

    while True:
        print("\nSecret Vault Operations:")
        print("1. Write secrets from JSON file")
        print("2. Manually enter secrets")
        print("3. Backup secrets and configuration")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            write_secrets_from_json(vault)
        elif choice == '2':
            manually_enter_secrets(vault)
        elif choice == '3':
            backup_secrets(vault)
        elif choice == '4':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()