import os
import json

def load_config():
    with open('libraries_config.json', 'r') as f:
        return json.load(f)

def update_symbol_library_table(library_changes):
    sym_lib_table_path = r'C:\Program Files\KiCad\8.0\share\kicad\template\sym-lib-table'
    
    # Load the current sym-lib-table file
    with open(sym_lib_table_path, 'r') as f:
        sym_lib_table_content = f.read()
    
    # Find and replace or remove entries based on the library_changes
    modified_content = sym_lib_table_content
    for old_name in library_changes['rename_z']:
        new_name = "z-" + old_name
        modified_content = modified_content.replace(f"(name \"{old_name}\")", f"(name \"{new_name}\")")
        modified_content = modified_content.replace(f"(uri \"${{KICAD8_SYMBOL_DIR}}/{old_name}.kicad_sym\")", f"(uri \"${{KICAD8_SYMBOL_DIR}}/z-{old_name}.kicad_sym\")")
    
    for delete_lib in library_changes['delete']:
        modified_content = modified_content.replace(f"(name \"{delete_lib}\")", "")
    
    # Write the modified content back to the sym-lib-table file
    with open(sym_lib_table_path, 'w') as f:
        f.write(modified_content)

def modify_kicad_libraries():
    config = load_config()
    update_symbol_library_table(config)

if __name__ == "__main__":
    modify_kicad_libraries()
