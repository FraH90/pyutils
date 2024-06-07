import os
import json

# Define the path to the KiCad symbols library directory
symbols_dir = r'C:\Program Files\KiCad\8.0\share\kicad\symbols'

# Load the JSON configuration file
with open('libraries_config.json', 'r') as f:
    config = json.load(f)

# Get the lists of libraries to delete and rename
libraries_to_delete = config.get('delete', [])
libraries_to_rename_z = config.get('rename_z', [])

# Delete specified libraries
for library in libraries_to_delete:
    library_path = os.path.join(symbols_dir, f"{library}.kicad_sym")
    if os.path.exists(library_path):
        os.remove(library_path)
        print(f"Deleted {library_path}")
    else:
        print(f"{library_path} not found")

# Rename specified libraries by prefixing with 'z'
for library in libraries_to_rename_z:
    old_library_path = os.path.join(symbols_dir, f"{library}.kicad_sym")
    if os.path.exists(old_library_path):
        new_library_path = os.path.join(symbols_dir, f"z{library}.kicad_sym")
        os.rename(old_library_path, new_library_path)
        print(f"Renamed {old_library_path} to {new_library_path}")
    else:
        print(f"{old_library_path} not found")
