import os
import sys
import ctypes

class AdminExecutor:
    def __init__(self, script_path):
        self.script_path = script_path

    @staticmethod
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def run(self):
        if self.is_admin():
            # If running as admin, execute the script
            with open(self.script_path, 'r') as file:
                exec(file.read())
        else:
            # If not admin, re-run the script with elevated privileges
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, self.script_path, None, 1)

if __name__ == "__main__":
    # Get the path of the current script
    current_script = os.path.abspath(__file__)
    
    # Create an instance of AdminExecutor with the current script path
    executor = AdminExecutor(current_script)
    
    # Run the script
    executor.run()