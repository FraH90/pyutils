import subprocess
import sys
import os
import json
from datetime import datetime

def find_python_installations():
    installations = []

    try:
        if sys.platform == 'win32':
            output = subprocess.check_output('where python', shell=True, text=True)
        else:
            output = subprocess.check_output('which -a python python3', shell=True, text=True)
        
        installations = output.strip().split('\n')
        installations = [path for path in installations if os.path.isfile(path) and os.access(path, os.X_OK)]
    except subprocess.CalledProcessError:
        pass

    return installations

def select_python_installation(installations):
    print("Found the following Python installations:")
    for i, installation in enumerate(installations):
        print(f"{i}: {installation}")
    
    while True:
        choice = input("Select the number of the Python installation to use: ")
        if choice.isdigit() and 0 <= int(choice) < len(installations):
            return installations[int(choice)]
        else:
            print("Invalid choice. Please try again.")

def install_packages(python_executable, package_list):
    for package in package_list:
        try:
            subprocess.check_call([python_executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {package}: {e}")

def print_installed_packages():
    try:
        output = subprocess.check_output([sys.executable, "-m", "pip", "list", "--format=json"], text=True)
        installed_packages = json.loads(output)
        installed_packages.sort(key=lambda x: datetime.strptime(x["installed"], "%Y-%m-%dT%H:%M:%S"))
        
        print("Installed packages (from newest to oldest):")
        for package in installed_packages:
            print(f"{package['name']} ({package['version']})")
    except Exception as e:
        print(f"Failed to get list of installed packages: {e}")

def main():
    installations = find_python_installations()
    if not installations:
        print("No Python installations found.")
        sys.exit(1)
    
    python_executable = select_python_installation(installations)
    
    json_file = "packages.json"
    if not os.path.isfile(json_file):
        print(f"JSON file '{json_file}' not found.")
        sys.exit(1)
    
    with open(json_file, "r") as file:
        package_list = json.load(file)
    
    if not isinstance(package_list, list):
        print("JSON file should contain a list of packages.")
        sys.exit(1)
    
    install_packages(python_executable, package_list)
    print_installed_packages()
    
if __name__ == "__main__":
    main()
