from setuptools import setup, find_packages

setup(
    name="choc_an_simulator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={"choc_an_simulator": ["storage"]},
)
