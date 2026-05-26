from setuptools import setup, find_packages

setup(
    name="snapclass",
    version="0.1.0",
    description="AI-powered attendance system using face & voice recognition",
    packages=find_packages(where="src"),
    package_dir={"": "src"},         
    python_requires=">=3.10",
    install_requires=[],               
)
