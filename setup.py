import subprocess
import sys
from setuptools import setup, find_packages

package_name = "datamorphers"
github_url = "git+https://github.com/davideganna/DataMorph.git"

# Check if the package is installed
if subprocess.run(
    [sys.executable, "-m", "pip", "show", package_name], capture_output=True, text=True
).stdout:
    print(f"Uninstalling {package_name}...")
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", package_name])

# Install the package from GitHub
print(f"Installing {package_name} from GitHub...")
subprocess.run([sys.executable, "-m", "pip", "install", github_url])
