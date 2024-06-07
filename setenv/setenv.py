import os
import sys
import platform

if len(sys.argv) != 3:
    print("Usage: python set_env.py ENV_VARIABLE_NAME env_variable_value")
    sys.exit(1)

env_variable_name = sys.argv[1]
env_variable_value = sys.argv[2]

if platform.system() == "Windows":
    import winreg
    
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, env_variable_name, 0, winreg.REG_EXPAND_SZ, env_variable_value)
        winreg.CloseKey(key)
        os.system(f"setx {env_variable_name} {env_variable_value}")
        print(f"Environment variable '{env_variable_name}' set to '{env_variable_value}' on Windows.")
    except WindowsError as e:
        print(f"Error setting environment variable: {e}")
        sys.exit(1)
        
elif platform.system() == "Linux":
    try:
        with open(os.path.expanduser("~/.bashrc"), "a") as bashrc:
            bashrc.write(f"\nexport {env_variable_name}='{env_variable_value}'\n")
        os.system(f"export {env_variable_name}='{env_variable_value}'")
        print(f"Environment variable '{env_variable_name}' set to '{env_variable_value}' on Linux.")
    except IOError as e:
        print(f"Error setting environment variable: {e}")
        sys.exit(1)
        
else:
    print(f"Unsupported operating system: {platform.system()}")
    sys.exit(1)
