import subprocess
import sys
import pkg_resources
from setuptools import setup, find_packages

package_name = "datamorphers"

# Check if the package is installed
installed_packages = {pkg.key for pkg in pkg_resources.working_set}
if package_name in installed_packages:
    subprocess.run(
        [sys.executable, "-m", "pip", "uninstall", "-y", package_name],
        check=False,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name=package_name,
    version="0.1",
    packages=find_packages(),
    install_requires=requirements,
)
