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
    
    functions_table = f"<h2 id='{module_name}'>{module_name} Module - Functions</h2>\n<table>\n<tr><th>Function</th></tr>\n"
    classes_table = f"<h2>{module_name} Module - Classes</h2>\n<table>\n<tr><th>Class</th></tr>\n"
    
    functions.sort()
    classes.sort()
    
    categorized_functions = {}
    categorized_classes = {}
    
    for func in functions:
        letter = func[0].upper()
        if letter not in categorized_functions:
            categorized_functions[letter] = []
        categorized_functions[letter].append(func)
    
    for cls in classes:
        letter = cls[0].upper()
        if letter not in categorized_classes:
            categorized_classes[letter] = []
        categorized_classes[letter].append(cls)
    
    for letter in sorted(categorized_functions.keys()):
        functions_table += f"<tr><th colspan='1'>{letter}</th></tr>\n"
        for func in categorized_functions[letter]:
            if is_standard_library(module_name):
                doc_link = f"https://docs.python.org/3/library/{module_name}.html#{module_name}.{quote(func)}"
            else:
                doc_link = get_module_documentation_link(module_name) or f"#{func}"
            functions_table += f"<tr><td><a href='{doc_link}'>{func}</a></td></tr>\n"
    
    for letter in sorted(categorized_classes.keys()):
        classes_table += f"<tr><th colspan='1'>{letter}</th></tr>\n"
        for cls in categorized_classes[letter]:
            if is_standard_library(module_name):
                doc_link = f"https://docs.python.org/3/library/{module_name}.html#{module_name}.{quote(cls)}"
            else:
                doc_link = get_module_documentation_link(module_name) or f"#{cls}"
            classes_table += f"<tr><td><a href='{doc_link}'>{cls}</a></td></tr>\n"
    
    functions_table += "</table>\n"
    classes_table += "</table>\n"
    
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
            </style>
        </head>
        <body>
        <h1>Python Modules Documentation</h1>
        <h2>Table of Contents</h2>
        <ul>
        """)

        for module_name in std_modules + ext_modules:
            if args.exclude_underscore and module_name.startswith("_"):
                continue
            f.write(f"<li><a href='#{module_name}'>{module_name}</a></li>\n")
        
        f.write("</ul>\n")

        for module_name in std_modules + ext_modules:
            if args.exclude_underscore and module_name.startswith("_"):
                continue
            functions_table, classes_table, error = generate_table_for_module(module_name, args.exclude_underscore_functions)
            if functions_table and classes_table:
                f.write("<div class='module-container'>\n")
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
