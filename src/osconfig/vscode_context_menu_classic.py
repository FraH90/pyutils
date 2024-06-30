from admin_executor import AdminExecutor
import os
import winreg as reg

def create_registry_key(base, path, name, value):
    try:
        key = reg.CreateKey(base, path)
        reg.SetValueEx(key, name, 0, reg.REG_SZ, value)
        reg.CloseKey(key)
        print(f"Successfully created/modified key: {path} - {name}")
    except Exception as e:
        print(f"Failed to create registry key {path} - {name}: {e}")

def main():
    # Path to VSCode executable
    current_user = os.getlogin()
    vscode_path = fr"C:\Users\{current_user}\AppData\Local\Programs\Microsoft VS Code\Code.exe"
    icon_path = vscode_path
    command_path = f'"{vscode_path}" "%V"'

    # Add to the new Windows 11 context menu for directories
    create_registry_key(reg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\Directory\Background\shell\VSCode", "MUIVerb", "Open with VSCode")
    create_registry_key(reg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\Directory\Background\shell\VSCode", "Icon", icon_path)
    create_registry_key(reg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\Directory\Background\shell\VSCode\command", "", command_path)

    # Add to the new Windows 11 context menu for files
    create_registry_key(reg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\*\shell\VSCode", "MUIVerb", "Open with VSCode")
    create_registry_key(reg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\*\shell\VSCode", "Icon", icon_path)
    create_registry_key(reg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\*\shell\VSCode\command", "", command_path)

    print("Registry keys creation process completed.")

if __name__ == "__main__":
    executor = AdminExecutor(__file__)
    executor.run()
    main()