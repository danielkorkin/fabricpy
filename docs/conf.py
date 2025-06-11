# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "fabricpy"
copyright = "2025, Daniel Korkin"
author = "Daniel Korkin"
release = "v0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # Core extension for auto-documentation
    "sphinx.ext.napoleon",  # Support for Google and NumPy style docstrings
    "sphinx.ext.viewcode",  # Add links to highlighted source code
    "sphinx.ext.autosummary",  # Generate summary tables of modules/classes
    "sphinx.ext.intersphinx",  # Link to other project's documentation
]

# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_type_aliases = None

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
    "show-inheritance": True,
}

# Autosummary settings
autosummary_generate = True

# Add type hints
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"

# Mock imports for documentation building (in case of missing dependencies)
autodoc_mock_imports = []

# Cross-reference resolution
add_module_names = False

# Intersphinx mapping for external documentation
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}

# Better handling of duplicate object descriptions
nitpicky = False
nitpick_ignore = []

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]

# Theme options for alabaster
html_theme_options = {
    "description": "A lightweight helper library for writing Fabric mods in Python",
    "github_user": "danielkorkin",
    "github_repo": "fabricpy",
    "github_banner": True,
    "github_button": True,
    "show_powered_by": False,
    "sidebar_width": "300px",
    "page_width": "1200px",
}
