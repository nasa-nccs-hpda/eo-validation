# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys
import importlib.metadata

sys.path.insert(0, os.path.abspath('..'))
# package_path = os.path.abspath('..')
# os.environ['PYTHONPATH'] = ':'.join((package_path, os.environ.get('PYTHONPATH', '')))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'eo-validation'
copyright = '2023, Jordan A. Caraballo-Vega'
author = 'Jordan A. Caraballo-Vega'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
    'jupyter_sphinx.execute',
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx_click.ext",
    "sphinx.ext.githubpages",
    "nbsphinx",
]

intersphinx_mapping = {
    "pyproj": ("https://pyproj4.github.io/pyproj/stable/", None),
    "rasterio": ("https://rasterio.readthedocs.io/en/stable/", None),
    "xarray": ("http://xarray.pydata.org/en/stable/", None),
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

source_suffix = ".rst"
master_doc = "index"

version = release = importlib.metadata.version('eo-validation')

pygments_style = "sphinx"

todo_include_todos = False

html_theme = 'sphinx_rtd_theme'

# html_static_path = ['_static/']
