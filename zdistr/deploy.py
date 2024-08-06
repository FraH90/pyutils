import os
import shutil
import subprocess
import sys
from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command.install import install
from wheel.bdist_wheel import bdist_wheel

class CustomWheel(bdist_wheel):
    def finalize_options(self):
        bdist_wheel.finalize_options(self)
        self.root_is_pure = False

class Deployer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.build_dir = self.project_root / 'zdistr' / 'build'
        self.dist_dir = self.project_root / 'zdistr' / 'dist'
        self.temp_clone_dir = self.build_dir / 'temp_clone'
        self.setup_py_path = self.build_dir / 'setup.py'
        self.manifest_path = self.project_root / 'zdistr' / 'MANIFEST.in'

    def run(self):
        self.check_git_status()
        self.clean_build_dir()
        self.clone_repo()
        self.get_package_info()
        self.create_setup_py()
        self.create_manifest_in()
        self.build_wheel()
        self.clean_temp_clone()

    def check_git_status(self):
        subprocess.run(['git', 'fetch'], cwd=self.project_root, check=True)
        local_status = subprocess.run(['git', 'status', '--porcelain'], cwd=self.project_root, text=True, capture_output=True)
        remote_status = subprocess.run(['git', 'status', '-uno'], cwd=self.project_root, text=True, capture_output=True)
        
        if local_status.stdout:
            print("You have uncommitted changes:")
            print(local_status.stdout)
        
        if remote_status.stdout:
            print("Your branch is behind the remote branch:")
            print(remote_status.stdout)

        if local_status.stdout or remote_status.stdout:
            proceed = input("Do you want to proceed anyway? (y/n): ").strip().lower()
            if proceed != 'y':
                sys.exit("Aborting deployment.")

    def clean_build_dir(self):
        if self.build_dir.exists():
            def remove_read_only(func, path, exc_info):
                import stat
                os.chmod(path, stat.S_IWRITE)
                func(path)
            
            shutil.rmtree(self.build_dir, onerror=remove_read_only)
        self.build_dir.mkdir(parents=True)

    def clone_repo(self):
        if self.temp_clone_dir.exists():
            shutil.rmtree(self.temp_clone_dir)
        subprocess.run(['git', 'clone', '.', str(self.temp_clone_dir)], cwd=self.project_root, check=True)
        for item in self.temp_clone_dir.iterdir():
            shutil.move(str(item), str(self.build_dir / item.name))

    def clean_temp_clone(self):
        if self.temp_clone_dir.exists():
            shutil.rmtree(self.temp_clone_dir)

    def get_package_info(self):
        self.package_name = input("Enter package name: ")
        self.version = input("Enter version: ")
        self.author = input("Enter author name: ")
        self.author_email = input("Enter author email: ")
        self.description = input("Enter package description: ")
        self.install_dir = input("Enter custom installation directory: ")

    def create_setup_py(self):
        setup_py_content_first_part = """
import os
from setuptools import setup, find_packages
from setuptools.command.install import install

class CustomInstall(install):
    def run(self):
        install.run(self)
        bin_dir = os.path.join(self.install_lib, 'bin')
        if os.path.exists(bin_dir):
            scripts_subfolders = [os.path.join(bin_dir, f) for f in os.listdir(bin_dir) if os.path.isdir(os.path.join(bin_dir, f))]
            for scripts_path in scripts_subfolders:
                self.add_to_path(scripts_path)

    def add_to_path(self, path):
        if os.name == 'nt':
            self.add_to_path_windows(path)
        else:
            self.add_to_path_unix(path)

    def add_to_path_windows(self, path):
        import winreg as reg
        reg_key = r'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment'
        try:
            reg_conn = reg.ConnectRegistry(None, reg.HKEY_LOCAL_MACHINE)
            reg_key = reg.OpenKey(reg_conn, reg_key, 0, reg.KEY_SET_VALUE)
            current_path, _ = reg.QueryValueEx(reg_key, 'Path')
            new_path = '{};{}'.format(current_path, path)
            reg.SetValueEx(reg_key, 'Path', 0, reg.REG_EXPAND_SZ, new_path)
            reg.CloseKey(reg_key)
        except Exception as e:
            print(f"Failed to set environment variable: {e}")

    def add_to_path_unix(self, path):
        shell = os.getenv('SHELL')
        rc_files = ['.bashrc', '.bash_profile', '.profile', '.zshrc']
        home_dir = os.path.expanduser('~')
        path_export = 'export PATH=$PATH:{}'.format(path)
        for rc_file in rc_files:
            rc_path = os.path.join(home_dir, rc_file)
            if os.path.exists(rc_path):
                with open(rc_path, 'a') as f:
                    f.write('\\n{}\\n'.format(path_export))
                break
"""

        setup_py_content_second_part = """
setup(
    name='{name}',
    version='{version}',
    author='{author}',
    author_email='{author_email}',
    description='{description}',
    packages=find_packages(),
    include_package_data=True,
    cmdclass={{'install': CustomInstall}},
)
        """.format(
            name=self.package_name,
            version=self.version,
            author=self.author,
            author_email=self.author_email,
            description=self.description
        )

        self.setup_py_content = setup_py_content_first_part + setup_py_content_second_part

        with open(self.setup_py_path, 'w') as f:
            f.write(self.setup_py_content)

    def create_manifest_in(self):
        manifest_content = """
# Include everything in the build directory
recursive-include build *

# Include specific files and directories
include README.md
include setup.py
        """
        with open(self.manifest_path, 'w') as f:
            f.write(manifest_content)
        print(f"Created MANIFEST.in at {self.manifest_path}")

    def build_wheel(self):
        zdistr_dir = self.project_root / 'zdistr' 
        os.chdir(build_dir)
        print(f"Building wheel in directory: {zdistr_dir}")
        subprocess.run([sys.executable, 'setup.py', 'bdist_wheel', '-d', str(self.dist_dir)], check=True)
        print(f"Wheel file should be in: {self.dist_dir}")

if __name__ == "__main__":
    deployer = Deployer()
    deployer.run()
