import inspect
import pkgutil
import importlib
import traceback

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
        return None, str(e)
    except Exception as e:
        return None, str(e)

    functions, classes = get_module_functions_and_classes(module)
    
    table = f"## {module_name} Module\n\n"
    table += "| Functions | Classes |\n"
    table += "| --- | --- |\n"
    
    max_length = max(len(functions), len(classes))
    for i in range(max_length):
        function = functions[i] if i < len(functions) else ""
        cls = classes[i] if i < len(classes) else ""
        table += f"| {function} | {cls} |\n"

    return table, None

def main():
    all_modules = sorted([modname for importer, modname, ispkg in pkgutil.iter_modules()])
    errors = []

    with open("python_modules_tables.md", "w") as f:
        for module_name in all_modules:
            table, error = generate_table_for_module(module_name)
            if table:
                f.write(table + "\n\n")
            if error:
                errors.append(f"Error importing module {module_name}: {error}")
    
    if errors:
        with open("import_errors.log", "w") as error_file:
            for error in errors:
                error_file.write(error + "\n")

if __name__ == "__main__":
    main()
