import re
from setuptools import setup

with open("anonymize_it/_version.py") as f:
    __version__ = re.search(r"__version__\s*=\s*[\"']([0-9.a-z]+)[\"']", f.read()).group(1)

with open("requirements.txt") as f:
    install_requires = [req.strip() for req in f.read().split("\n") if req.strip()]

setup(
    name="anonymize-it",
    author="Elastic",
    author_email="support@elastic.co",
    version=__version__,
    packages=["anonymize_it"],
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "anonymize-it=anonymize_it.cli:main"
        ]
    }
)
