import os
import json

SYM_LIB_TABLE_PATH = r'C:\Users\caterina\AppData\Roaming\kicad\8.0\sym-lib-table'       # path to the KiCad symbol table
JSON_CONFIG = os.path.join('config', 'libraries_config.json')                                    # path to the json config file
SYMBOLS_DIR = r'C:\Program Files\KiCad\8.0\share\kicad\symbols'                             # path to the KiCad symbols library directory

def load_config(json_config):
    with open(json_config, 'r') as f:
        return json.load(f)

def write_library_files(config):

    # Get the lists of libraries to delete and rename
    libraries_to_delete = config.get('delete', [])
    libraries_to_rename_z = config.get('rename_z', [])

    # Delete specified libraries
    for library in libraries_to_delete:
        library_path = os.path.join(SYMBOLS_DIR, f"{library}.kicad_sym")
        if os.path.exists(library_path):
            os.remove(library_path)
            print(f"Deleted {library_path}")
        else:
            print(f"{library_path} not found")

    # Rename specified libraries by prefixing with 'z'
    for library in libraries_to_rename_z:
        old_library_path = os.path.join(SYMBOLS_DIR, f"{library}.kicad_sym")
        if os.path.exists(old_library_path):
            new_library_path = os.path.join(SYMBOLS_DIR, f"z{library}.kicad_sym")
            os.rename(old_library_path, new_library_path)
            print(f"Renamed {old_library_path} to {new_library_path}")
        else:
            print(f"{old_library_path} not found")


def update_symbol_library_table(config):
    # Load the current sym-lib-table file
    with open(SYM_LIB_TABLE_PATH, 'r') as f:
        sym_lib_table_content = f.read()
    
    # Split the content into lines for easier processing
    lines = sym_lib_table_content.split('\n')
    
    # Prepare a new list to hold modified lines
    modified_lines = []

    # Process each line
    for line in lines:
        # Check for libraries to rename
        if any(f'(name "{lib}")' in line for lib in config['rename_z']):
            for lib in config['rename_z']:
                if f'(name "{lib}")' in line:
                    new_line = line.replace(f'(name "{lib}")', f'(name "z-{lib}")')
                    new_line = new_line.replace(f'/{lib}.kicad_sym', f'/z-{lib}.kicad_sym')
                    modified_lines.append(new_line)
                    break
        # Check for libraries to delete
        elif any(f'(name "{lib}")' in line for lib in config['delete']):
            for lib in config['delete']:
                if f'(name "{lib}")' in line:
                    # Skip this line to delete the library
                    break
        else:
            # For all other lines, keep them unchanged
            modified_lines.append(line)
    
    # Join the modified lines back into a single string
    modified_content = '\n'.join(modified_lines)
    
    # Write the modified content back to the sym-lib-table file
    with open(SYM_LIB_TABLE_PATH, 'w') as f:
        f.write(modified_content)


if __name__ == "__main__":
    config = load_config(JSON_CONFIG)
    write_library_files(config)
    update_symbol_library_table(config)

