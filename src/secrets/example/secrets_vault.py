import os
import json
import base64
import secrets
import zlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
import winreg
import shutil

class SecretsVault:
    _instance = None

    def __init__(self, config_dir=None, salt_filename='salt.bin', password_filename='secret_password.bin', env_var_name='ENCRYPTED_SECRETS'):
        self.config_dir = config_dir or os.path.expanduser('~/.secrets_manager')
        os.makedirs(self.config_dir, exist_ok=True)
        self.salt_path = os.path.join(self.config_dir, salt_filename)
        self.password_path = os.path.join(self.config_dir, password_filename)
        self.env_var_name = env_var_name
        self.key = self._setup_encryption()
        self.secrets_data = None
        self._cached_encrypted = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _setup_encryption(self):
        salt = self._get_or_create_salt()
        password = self._get_or_create_password()
        kdf = Scrypt(
            salt=salt,
            length=32,
            n=2**20,  # High cost factor for increased security
            r=8,
            p=1,
            backend=default_backend()
        )
        return kdf.derive(password)

    def _get_or_create_salt(self):
        try:
            with open(self.salt_path, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            salt = os.urandom(16)
            with open(self.salt_path, 'wb') as f:
                f.write(salt)
            return salt

    def _get_or_create_password(self):
        try:
            with open(self.password_path, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            password = secrets.token_bytes(32)  # 256-bit password
            with open(self.password_path, 'wb') as f:
                f.write(password)
            return password

    def _encrypt(self, data):
        compressed_data = zlib.compress(data.encode('utf-8'))
        nonce = os.urandom(12)
        aesgcm = AESGCM(self.key)
        encrypted = aesgcm.encrypt(nonce, compressed_data, None)
        return base64.b64encode(nonce + encrypted).decode('utf-8')

    def _decrypt(self, encrypted_data):
        decoded = base64.b64decode(encrypted_data)
        nonce, ciphertext = decoded[:12], decoded[12:]
        aesgcm = AESGCM(self.key)
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)
        return zlib.decompress(decrypted).decode('utf-8')

    def _set_windows_env_var(self, name, value):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
            winreg.CloseKey(key)
        except Exception as e:
            raise RuntimeError(f"Error setting environment variable: {e}")

    def _get_windows_env_var(self, name):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, name)
            winreg.CloseKey(key)
            return value
        except FileNotFoundError:
            return None

    def encrypt_and_store(self, data):
        json_data = json.dumps(data)
        encrypted = self._encrypt(json_data)
        self._cached_encrypted = encrypted
        self._set_windows_env_var(self.env_var_name, encrypted)

    def decrypt_and_load(self):
        if self._cached_encrypted:
            encrypted = self._cached_encrypted
        else:
            encrypted = self._get_windows_env_var(self.env_var_name)
        
        if not encrypted:
            self.secrets_data = {'services': {}}
        else:
            decrypted = self._decrypt(encrypted)
            self.secrets_data = json.loads(decrypted)

    def get_secret(self, service, key):
        if self.secrets_data is None:
            self.decrypt_and_load()
        return self.secrets_data.get('services', {}).get(service, {}).get(key)

    def get_all_secrets_for_service(self, service):
        if self.secrets_data is None:
            self.decrypt_and_load()
        return self.secrets_data.get('services', {}).get(service, {})

    def get_all_services(self):
        if self.secrets_data is None:
            self.decrypt_and_load()
        return list(self.secrets_data.get('services', {}).keys())

    def add_or_update_secret(self, service, key, value):
        if self.secrets_data is None:
            self.decrypt_and_load()
        if 'services' not in self.secrets_data:
            self.secrets_data['services'] = {}
        if service not in self.secrets_data['services']:
            self.secrets_data['services'][service] = {}
        self.secrets_data['services'][service][key] = value
        self.encrypt_and_store(self.secrets_data)

    def remove_secret(self, service, key):
        if self.secrets_data is None:
            self.decrypt_and_load()
        if service in self.secrets_data.get('services', {}) and key in self.secrets_data['services'][service]:
            del self.secrets_data['services'][service][key]
            if not self.secrets_data['services'][service]:
                del self.secrets_data['services'][service]
            self.encrypt_and_store(self.secrets_data)
        else:
            raise KeyError(f"Secret '{key}' not found for service '{service}'.")

    def load_from_json(self, json_file_path):
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        self.encrypt_and_store(data)

    def add_or_update_multiple_secrets(self, new_secrets):
        if self.secrets_data is None:
            self.decrypt_and_load()
        for service, secrets in new_secrets.items():
            if service not in self.secrets_data['services']:
                self.secrets_data['services'][service] = {}
            self.secrets_data['services'][service].update(secrets)
        self.encrypt_and_store(self.secrets_data)

    def export_secrets(self):
        self.decrypt_and_load()
        return json.dumps(self.secrets_data, indent=2)

    def get_saltpsw_path(self):
        return {
            'salt': self.salt_path,
            'password': self.password_path
        }

""" 
# Usage example
if __name__ == "__main__":
    manager = SecretsVault.get_instance()

    # Load secrets from a JSON file
    manager.load_from_json('secrets.json')

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

    # Add or update a secret
    manager.add_or_update_secret('new_service', 'api_key', 'new_api_key_value')

    # Remove a secret
    manager.remove_secret('old_service', 'old_key')

    # Add multiple secrets at once
    new_secrets = {
        'database': {
            'host': 'new_db.example.com',
            'port': 5433,
            'username': 'new_admin_user',
            'password': 'new_v3ry_s3cur3_p@ssw0rd'
        },
        'aws': {
            'access_key_id': 'NEWAKIAIOSFODNN7EXAMPLE',
            'secret_access_key': 'NEWwJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
        }
    }
    manager.add_or_update_multiple_secrets(new_secrets) """