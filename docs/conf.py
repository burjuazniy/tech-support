# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
import os

# Make the backend package importable without installing it.
sys.path.insert(0, os.path.abspath("../back/src"))

# -- Project information -------------------------------------------------------

project = "Tech Support"
copyright = "2026, burjuazniy"
author = "burjuazniy"
release = "0.1.0"

# -- General configuration -----------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",       # pull docstrings from source code
    "sphinx.ext.napoleon",      # support Google & NumPy docstring styles
    "sphinx.ext.viewcode",      # add links to highlighted source
    "sphinx.ext.intersphinx",   # cross-reference to Python stdlib docs
]

# Napoleon settings – we use Google style.
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False

# autodoc settings
autodoc_member_order = "bysource"
autodoc_typehints = "description"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output ---------------------------------------------------

html_theme = "alabaster"
html_static_path = ["_static"]
