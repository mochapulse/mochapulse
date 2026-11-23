"""Static configuration: environment, filesystem paths, and color themes.

All values are resolved once at import time. Paths are anchored to the
repository root (the parent of this package directory) so the script behaves
identically regardless of the current working directory, while the per-user
cache keeps its historic ``cache/<sha256>.txt`` location.

Environment variables:
    ACCESS_TOKEN (str): GitHub personal access token for the GraphQL API.
    USER_NAME (str): GitHub username to query (default: ``mochapulse``).
"""
import datetime
import hashlib
import os
from collections import namedtuple

# Repository root = parent of this package directory. Built artifacts and the
# ASCII art file live here; the cache lives in ``<root>/cache``.
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(PACKAGE_DIR)

ASCII_ART_FILE = os.path.join(PROJECT_ROOT, "mochapulse-ascii-art.txt")
DARK_SVG_FILE = os.path.join(PROJECT_ROOT, "dark_mode.svg")
LIGHT_SVG_FILE = os.path.join(PROJECT_ROOT, "light_mode.svg")

# GitHub API configuration.
GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "")
USER_NAME = os.environ.get("USER_NAME", "mochapulse")
API_HEADERS = {"authorization": "token " + ACCESS_TOKEN} if ACCESS_TOKEN else {}
HAS_TOKEN = bool(ACCESS_TOKEN)

# Account birth date used to render the "Uptime" age string.
BIRTHDAY = datetime.datetime(2001, 6, 28)

# Number of human-written comment lines at the top of every cache file. The
# cache contract (see AGENTS.md) fixes this header size.
CACHE_COMMENT_LINES = 7

# Minimum SVG canvas width in pixels; the card grows past this only if the
# art/info panels need more room.
SVG_MIN_WIDTH = 1160


def user_cache_path():
    """Return the absolute path to the current user's LOC/commit cache file.

    The file name is the SHA-256 of ``USER_NAME`` so each queried user gets an
    isolated cache. Kept under ``<repo>/cache`` to match the committed layout.

    :return: Absolute path to ``<repo>/cache/<sha256>.txt``.
    :rtype: str
    """
    digest = hashlib.sha256(USER_NAME.encode("utf-8")).hexdigest()
    return os.path.join(PROJECT_ROOT, "cache", digest + ".txt")


# A color theme for one SVG variant. ``add``/``del_`` color the LOC +/- counts;
# ``del_`` is spelled with a trailing underscore because ``del`` is a keyword.
Theme = namedtuple("Theme", "bg fg key value neutral add del_")

DARK_THEME = Theme(
    bg="#0d1117",
    fg="#c9d1d9",
    key="#ffa657",
    value="#a5d6ff",
    neutral="#555d66",
    add="#3fb950",
    del_="#f85149",
)

LIGHT_THEME = Theme(
    bg="#f6f8fa",
    fg="#24292f",
    key="#953800",
    value="#0a3069",
    neutral="#c0c8d4",
    add="#1a7f37",
    del_="#cf222e",
)
