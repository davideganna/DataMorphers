# pip uninstall datamorphers -y
# pip install -e .

import subprocess
import sys
from setuptools import setup, find_packages

package_name = "datamorphers"

subprocess.run(
    [sys.executable, "-m", "pip", "uninstall", "-y", package_name], check=False
)

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name=package_name,
    version="0.1",
    packages=find_packages(),
    install_requires=requirements,
)
