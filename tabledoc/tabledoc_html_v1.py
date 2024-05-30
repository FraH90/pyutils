import pkgutil
import os
import sys
import subprocess
import importlib
import inspect
from urllib.parse import quote

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

def get_module_functions_and_classes(module):
    functions = []
    classes = []
    for name, member in inspect.getmembers(module):
        if inspect.isfunction(member):
            functions.append(name)
        elif inspect.isclass(member):
            classes.append(name)
    return functions, classes

def generate_table_for_module(module_name):
    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        return None, None, str(e)
    except Exception as e:
        return None, None, str(e)

    functions, classes = get_module_functions_and_classes(module)
    
    functions_table = f"<h2>{module_name} Module - Functions</h2>\n<table>\n<tr><th>Function</th></tr>\n"
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
            doc_link = f"https://docs.python.org/3/library/{module_name}.html#{module_name}.{quote(func)}"
            functions_table += f"<tr><td><a href='{doc_link}'>{func}</a></td></tr>\n"
    
    for letter in sorted(categorized_classes.keys()):
        classes_table += f"<tr><th colspan='1'>{letter}</th></tr>\n"
        for cls in categorized_classes[letter]:
            doc_link = f"https://docs.python.org/3/library/{module_name}.html#{module_name}.{quote(cls)}"
            classes_table += f"<tr><td><a href='{doc_link}'>{cls}</a></td></tr>\n"
    
    functions_table += "</table>\n"
    classes_table += "</table>\n"
    
    return functions_table, classes_table, None

def main():
    installations = find_python_installations()
    selected_python = select_python_installation(installations)
    sys.executable = selected_python

    all_modules = sorted([modname for importer, modname, ispkg in pkgutil.iter_modules()])
    errors = []

    with open("python_modules_tables.html", "w") as f:
        f.write("<html><head><title>Python Modules Documentation</title></head><body>\n")
        for module_name in all_modules:
            functions_table, classes_table, error = generate_table_for_module(module_name)
            if functions_table and classes_table:
                f.write(functions_table + "\n")
                f.write(classes_table + "\n")
            if error:
                errors.append(f"Error importing module {module_name}: {error}")
        f.write("</body></html>\n")
    
    if errors:
        with open("import_errors.log", "w") as error_file:
            for error in errors:
                error_file.write(error + "\n")

if __name__ == "__main__":
    main()
