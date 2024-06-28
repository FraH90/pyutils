import pkgutil
import os
import sys
import subprocess
import importlib
import inspect
from urllib.parse import quote
import argparse

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

def get_module_functions_and_classes(module, exclude_underscore):
    functions = []
    classes = []
    for name, member in inspect.getmembers(module):
        if exclude_underscore and name.startswith('_'):
            continue
        if inspect.isfunction(member):
            functions.append(name)
        elif inspect.isclass(member):
            classes.append(name)
    return functions, classes

def is_standard_library(module_name):
    if module_name in sys.builtin_module_names:
        return True
    module = importlib.util.find_spec(module_name)
    if module is not None and module.origin is not None:
        return 'site-packages' not in module.origin
    return False

def get_module_documentation_link(module_name):
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, '__doc__') and module.__doc__:
            return module.__doc__.split('\n')[0]
    except ImportError:
        return None
    return None

def generate_table_for_module(module_name, exclude_underscore):
    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        return None, None, str(e)
    except Exception as e:
        return None, None, str(e)

    functions, classes = get_module_functions_and_classes(module, exclude_underscore)
    
    functions.sort()
    classes.sort()
    
    def create_table(items, item_type):
        table = f"<h2 id='{module_name}-{item_type}'>{module_name} Module - {item_type.capitalize()}</h2>\n<table>\n"
        columns = 3
        for i in range(0, len(items), columns):
            table += "<tr>"
            for j in range(columns):
                if i + j < len(items):
                    item = items[i + j]
                    if is_standard_library(module_name):
                        doc_link = f"https://docs.python.org/3/library/{module_name}.html#{module_name}.{quote(item)}"
                    else:
                        doc_link = get_module_documentation_link(module_name) or f"#{item}"
                    table += f"<td><a href='{doc_link}'>{item}</a></td>"
                else:
                    table += "<td></td>"
            table += "</tr>\n"
        table += "</table>\n"
        return table
    
    functions_table = create_table(functions, "functions")
    classes_table = create_table(classes, "classes")
    
    return functions_table, classes_table, None

def main():
    parser = argparse.ArgumentParser(description="Generate documentation for Python modules.")
    parser.add_argument("--exclude-underscore", action="store_true", help="Exclude modules that start with an underscore.")
    parser.add_argument("-e", "--exclude-underscore-functions", action="store_true", help="Exclude functions and classes that start with an underscore.")
    args = parser.parse_args()

    installations = find_python_installations()
    selected_python = select_python_installation(installations)
    sys.executable = selected_python

    all_modules = sorted([modname for importer, modname, ispkg in pkgutil.iter_modules()])
    std_modules = sorted([mod for mod in all_modules if is_standard_library(mod)])
    ext_modules = sorted([mod for mod in all_modules if not is_standard_library(mod)])
    errors = []

    with open("python_modules_tables.html", "w") as f:
        f.write("""
        <html>
        <head>
            <title>Python Modules Documentation</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                }
                h2 {
                    color: #333;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }
                th, td {
                    padding: 10px;
                    border: 1px solid #ddd;
                }
                th {
                    background-color: #f4f4f4;
                }
                tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
                a {
                    color: #007BFF;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
                .module-container {
                    display: flex;
                    flex-direction: row;
                }
                .module-container > div {
                    flex: 1;
                    margin-right: 20px;
                }
                .module-link {
                    margin: 10px 0;
                    display: block;
                }
                .toc-table {
                    width: 100%;
                    table-layout: fixed;
                }
                .toc-table td {
                    padding: 2px 5px;
                    border: 1px solid #ddd;
                }
            </style>
        </head>
        <body>
        <h1>Python Modules Documentation</h1>
        <h2>Table of Contents</h2>
        """)

        def write_toc_table(modules, title):
            f.write(f"<h3>{title}</h3>\n<table class='toc-table'>\n")
            columns = 8
            for i in range(0, len(modules), columns):
                f.write("<tr>")
                for j in range(columns):
                    if i + j < len(modules):
                        module = modules[i + j]
                        f.write(f"<td><a href='#{module}'>{module}</a></td>")
                    else:
                        f.write("<td></td>")
                f.write("</tr>\n")
            f.write("</table>\n")

        write_toc_table(std_modules, "Standard Library Modules")
        write_toc_table(ext_modules, "External Modules")

        for module_name in std_modules + ext_modules:
            if args.exclude_underscore and module_name.startswith("_"):
                continue
            functions_table, classes_table, error = generate_table_for_module(module_name, args.exclude_underscore_functions)
            if functions_table and classes_table:
                f.write(f"<div class='module-container' id='{module_name}'>\n")
                f.write(f"<div>{functions_table}</div>\n")
                f.write(f"<div>{classes_table}</div>\n")
                f.write("</div>\n")
            if error:
                errors.append(f"Error importing module {module_name}: {error}")
        
        f.write("</body></html>\n")
    
    if errors:
        with open("import_errors.log", "w") as error_file:
            for error in errors:
                error_file.write(error + "\n")

if __name__ == "__main__":
    main()
