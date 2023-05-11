from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["ipython>=6", "nbformat>=4", "nbconvert>=5", "requests>=2"]

setup(
    name="eo-validation",
    version="0.0.1",
    author="Jordan A. Caraballo-Vega",
    author_email="jordan.a.caraballo-vega@nasa.gov",
    description="Collaborative validation tools for remote sensing imagery",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/nasa-nccs-hpda/eo-validation",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)