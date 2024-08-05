## Intro
The goal of this project is to implement a system that can write stuff like API keys, tokens, password etc of online services in an environment variable of the OS, in an encripted form, in order to access it later in a programmatical way from a python script.
The system let both write stuff into the environment variable, and read from it.

The base of everything is the class SecretsVault, which implement an object that contain the data we're interested into in JSON form; you can load data from a json file, encrypt them, and store them in the environment variable designed to store the data.
Or you could read the encrypted data from the environment variable, decript them, and retrieve the API key/password/token you need. All of this from a python script, that load the secrets_vault module and use its class SecretsVault.

The secrets_manager.py script instead employ some functions that simplify writing/reading stuff into the environment variable by using the SecretsVault class.
So basically:
- use the SecretsVault class in secrets_vault.py when you need to access to the API keys/tokens from the environment variable in a programmatic way
- use the secrets_manager.py script when you want to write new data into the environment variable, dump the informations in it as a json file, etc. Obviously you need to provide the crypto credentials in order to encrypt/decrypt the data. The encription credentials are stored into ~/.secrets_manager (salt file, psw file).
You can backup those by using the preposed function employed in secrets_manager.