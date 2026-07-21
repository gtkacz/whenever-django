"""Sphinx configuration for whenever-django."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import whenever_django  # noqa: E402

project = "whenever-django"
author = "Gabriel Mitelman Tkacz"
copyright = "2026, Gabriel Mitelman Tkacz"
version = whenever_django.__version__
release = whenever_django.__version__

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
]

source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}
root_doc = "index"
exclude_patterns = [
    "_build",
    "plans/**",
    "brainstorms/**",
    "ideation/**",
    "Thumbs.db",
    ".DS_Store",
    "**/task_plan.md",
    "**/findings.md",
    "**/progress.md",
    "**/*brainstorm*",
    "**/*ideation*",
]

autosummary_generate = True
autodoc_member_order = "bysource"
autodoc_typehints = "description"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "django": ("https://docs.djangoproject.com/en/5.2/", None),
    "whenever": ("https://whenever.readthedocs.io/en/latest/", None),
}

myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 3

html_theme = "furo"
html_title = "whenever-django"
html_baseurl = "https://python-whenever.github.io/whenever-django/"
html_theme_options = {
    "source_repository": "https://github.com/python-whenever/whenever-django/",
    "source_branch": "main",
    "source_directory": "docs/",
}
