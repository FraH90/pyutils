import os
import json
import base64
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
import winreg

class SecretsManager:
    def __init__(self, salt_path='salt.bin', env_var_name='ENCRYPTED_SECRETS'):
        self.salt_path = salt_path
        self.env_var_name = env_var_name
        self.key = self._setup_encryption()
        self.secrets_data = None
        self._cached_encrypted = None

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
        password_path = 'secret_password.bin'
        try:
            with open(password_path, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            password = secrets.token_bytes(32)  # 256-bit password
            with open(password_path, 'wb') as f:
                f.write(password)
            return password

    def _encrypt(self, data):
        nonce = os.urandom(12)
        aesgcm = AESGCM(self.key)
        encrypted = aesgcm.encrypt(nonce, data.encode('utf-8'), None)
        return base64.b64encode(nonce + encrypted).decode('utf-8')

    def _decrypt(self, encrypted_data):
        decoded = base64.b64decode(encrypted_data)
        nonce, ciphertext = decoded[:12], decoded[12:]
        aesgcm = AESGCM(self.key)
        return aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')

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
                raise ValueError(f'Environment variable "{self.env_var_name}" not found or empty.')
            self._cached_encrypted = encrypted

        decrypted = self._decrypt(encrypted)
        self.secrets_data = json.loads(decrypted)

    def get_secret(self, key):
        if self.secrets_data is None:
            self.decrypt_and_load()
        return self.secrets_data.get(key)

    def add_or_update_secret(self, key, value):
        if self.secrets_data is None:
            self.decrypt_and_load()
        self.secrets_data[key] = value
        self.encrypt_and_store(self.secrets_data)

    def remove_secret(self, key):
        if self.secrets_data is None:
            self.decrypt_and_load()
        if key in self.secrets_data:
            del self.secrets_data[key]
            self.encrypt_and_store(self.secrets_data)
        else:
            raise KeyError(f"Secret '{key}' not found.")

    def load_from_json(self, json_file_path):
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        self.encrypt_and_store(data)

    def add_or_update_multiple_secrets(self, new_secrets):
        if self.secrets_data is None:
            self.decrypt_and_load()
        self.secrets_data.update(new_secrets)
        self.encrypt_and_store(self.secrets_data)


# Usage example
if __name__ == "__main__":
    manager = SecretsManager()
    
    # Load secrets from a JSON file and encrypt them
    manager.load_from_json('secrets.json')
    
    # Add a new secret
    manager.add_or_update_secret('new_api_key', 'abcdef123456')
    
    # Update an existing secret
    manager.add_or_update_secret('api_key', 'updated_key_value')
    
    # Add multiple secrets at once
    new_secrets = {
        'database_url': 'postgres://user:pass@localhost/db',
        'aws_access_key': 'AKIAIOSFODNN7EXAMPLE'
    }
    manager.add_or_update_multiple_secrets(new_secrets)
    
    # Remove a secret
    # manager.remove_secret('old_key')
    
    # Retrieve a specific secret
    api_key = manager.get_secret('api_key')
    print(f"API Key: {api_key}")
    
    # Print all secrets
    print("All secrets:")
    print(json.dumps(manager.secrets_data, indent=2))