#!/usr/bin/env python

import os
import sys

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(DOCS_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "src"))

project = "tango-frame"
copyright = "2026"
version = "0.1.0"
release = "0.1.0"
language = "en"
root_doc = "index"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "myst_parser",
]
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
myst_enable_extensions = [
    "colon_fence", "deflist", "attrs_block", "substitution", "linkify",
]
myst_linkify_fuzzy_links = True
myst_heading_anchors = 3
autosummary_generate = True
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}
add_module_names = False
autodoc_typehints = "description"
autodoc_preserve_defaults = True
set_type_checking_flag = True
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pytango": ("https://tango-controls.readthedocs.io/projects/pytango/en/latest/", None),
}
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "collapse_navigation": False,
    "navigation_depth": 4,
    "titles_only": False,
}
html_static_path = ["_static"] if os.path.isdir(os.path.join(DOCS_DIR, "_static")) else []
html_extra_path = ["robots.txt"] if os.path.isfile(os.path.join(DOCS_DIR, "robots.txt")) else []
