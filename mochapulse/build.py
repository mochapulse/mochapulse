"""Orchestrator: build both SVG cards, then fill them with GitHub stats.

Run via the repository-root shim ``today.py`` (``python today.py``), which the
CI workflow and the README both rely on.

Flow:
    1. Render ``dark_mode.svg`` / ``light_mode.svg`` with placeholder zeros.
    2. Compute the account age for the "Uptime" row.
    3. With a token, query the GitHub GraphQL API and inject live stats.
       Without one, reuse the last cached LOC/commit totals.

Degraded runs (missing token or an API error) fail the CI job on purpose so
zeroed/partial stats are never committed.
"""
import os
import sys

from . import config
from .age import format_age
from .github_api import fetch_follower_count, fetch_repos_or_stars, fetch_user
from .loc_cache import (build_loc_cache, cached_commit_total, cached_loc_totals,
                        sum_cached_commits)
from .metrics import QUERY_COUNT, print_timing, time_call
from .svg_card import build_svg_document, inject_stats, load_ascii_art


def _write_cards(ascii_lines):
    """Render and write both theme variants with placeholder stats.

    :param list ascii_lines: ASCII art lines for the left panel.
    """
    with open(config.DARK_SVG_FILE, "w") as f:
        f.write(build_svg_document(ascii_lines, config.DARK_THEME))
    sys.stdout.write("Wrote dark_mode.svg\n")
    with open(config.LIGHT_SVG_FILE, "w") as f:
        f.write(build_svg_document(ascii_lines, config.LIGHT_THEME))
    sys.stdout.write("Wrote light_mode.svg\n")


def _inject_both(age, commits, stars, repos, contributed, followers, loc):
    """Inject the same stats into both theme SVGs.

    :param str age: Age string.
    :param int commits: Commit count.
    :param int stars: Star count.
    :param int repos: Owned-repository count.
    :param int contributed: Contributed-repository count.
    :param int followers: Follower count.
    :param list loc: ``[additions, deletions, net_loc]``.
    """
    for svg_file in (config.DARK_SVG_FILE, config.LIGHT_SVG_FILE):
        inject_stats(svg_file, age, commits, stars, repos, contributed,
                     followers, loc)


def _apply_cached_fallback(age):
    """Fill both cards from the last cached totals (no API access).

    :param str age: Age string to display.
    """
    loc_fallback = cached_loc_totals(config.CACHE_COMMENT_LINES)
    commit_fallback = cached_commit_total(config.CACHE_COMMENT_LINES)
    _inject_both(age, commit_fallback, 0, 0, 0, 0, loc_fallback)


def run():
    """Build the cards and populate them with live or cached stats."""
    print("Calculation times:")

    ascii_lines = load_ascii_art()
    sys.stdout.write(f"Loaded {len(ascii_lines)} ascii lines\n")
    _write_cards(ascii_lines)

    age, age_time = time_call(format_age, config.BIRTHDAY)
    print_timing("age calculation", age_time)

    if not config.HAS_TOKEN:
        print("\n** No ACCESS_TOKEN configured. Skipping GitHub API queries. **")
        print("** Set ACCESS_TOKEN and USER_NAME secrets in repo settings. **")
        print("** Falling back to last cached LOC/commit stats. **\n")
        _apply_cached_fallback(age)
        if os.environ.get("GITHUB_ACTIONS") == "true":
            print("** Missing ACCESS_TOKEN in CI: failing the job so degraded "
                  "stats are not committed. **")
            sys.exit(1)
        return

    try:
        # Querying the user validates the token (and is counted); the returned
        # id/date are not needed downstream.
        _user, user_time = time_call(fetch_user, config.USER_NAME)
        print_timing("account data", user_time)

        total_loc, loc_time = time_call(
            build_loc_cache, ["OWNER", "COLLABORATOR", "ORGANIZATION_MEMBER"],
            config.CACHE_COMMENT_LINES)
        print_timing("LOC (cached)" if total_loc[-1] else "LOC (no cache)",
                     loc_time)

        commits, commit_time = time_call(sum_cached_commits,
                                         config.CACHE_COMMENT_LINES)
        print_timing("commits", commit_time)

        stars, star_time = time_call(fetch_repos_or_stars, "stars", ["OWNER"])
        print_timing("stars", star_time)

        repos, repo_time = time_call(fetch_repos_or_stars, "repos", ["OWNER"])
        print_timing("repos", repo_time)

        contributed, contrib_time = time_call(
            fetch_repos_or_stars, "repos",
            ["OWNER", "COLLABORATOR", "ORGANIZATION_MEMBER"])
        print_timing("contributed repos", contrib_time)

        followers, follower_time = time_call(fetch_follower_count,
                                             config.USER_NAME)
        print_timing("followers", follower_time)

        # Thousands-separate the additions/deletions/net LOC for display.
        for index in range(len(total_loc) - 1):
            total_loc[index] = "{:,}".format(total_loc[index])

        _inject_both(age, commits, stars, repos, contributed, followers,
                     total_loc[:-1])

        print("Total GitHub GraphQL API calls:",
              "{:>3}".format(sum(QUERY_COUNT.values())))
        for category, count in QUERY_COUNT.items():
            print("{:<28}".format("   " + category + ":"),
                  "{:>6}".format(count))
    except Exception as error:
        print(f"\n** GitHub API error: {error} **")
        print("** Falling back to last cached LOC/commit stats; failing the "
              "job so the zeroed SVG is not committed. **\n")
        _apply_cached_fallback(age)
        sys.exit(1)
