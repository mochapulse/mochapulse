"""Lines-of-code and commit accounting backed by an on-disk cache.

The cache (one file per user, see :func:`mochapulse.config.user_cache_path`)
stores one row per repository::

    <repo_sha256> <commit_count> <net_loc> <additions> <deletions>

preceded by a fixed block of human-written comment lines. Only repositories
whose commit count changed since the last run are re-fetched from the API,
which keeps the daily build cheap. This module depends on
:func:`mochapulse.github_api.post_graphql` but nothing in it depends back, so
there is no import cycle despite the fetch/cache interplay.
"""
import hashlib

import requests

from . import config
from .github_api import post_graphql
from .metrics import QUERY_COUNT, increment_query_count


def _repo_hash(name_with_owner):
    """Return the SHA-256 hex digest of a ``owner/name`` repository string.

    :param str name_with_owner: Repository identifier, e.g. ``"octocat/Hello"``.
    :return: Hex digest used as the stable row key in the cache.
    :rtype: str
    """
    return hashlib.sha256(name_with_owner.encode("utf-8")).hexdigest()


def fetch_repo_loc(owner, repo_name, cache_rows, cache_comment,
                   additions=0, deletions=0, commits=0, cursor=None):
    """Recursively sum additions, deletions, and commits for one repository.

    Walks every page of the default branch's commit history. On an API error
    the partial cache is flushed to disk so progress is not lost.

    :param str owner: Repository owner (user or organization).
    :param str repo_name: Repository name.
    :param list cache_rows: In-memory cache rows (saved on error).
    :param list cache_comment: Comment header lines (saved on error).
    :param int additions: Running total of added lines.
    :param int deletions: Running total of deleted lines.
    :param int commits: Running count of authored commits.
    :param str cursor: Pagination cursor for the next history page.
    :return: Triple ``(additions, deletions, commits)``, or ``0`` when the
        repository has no default branch.
    :rtype: tuple or int
    :raises Exception: On HTTP 403 (rate limit) or any other non-200 status.
    """
    increment_query_count("fetch_repo_loc")
    query = """
    query ($repo_name: String!, $owner: String!, $cursor: String) {
        repository(name: $repo_name, owner: $owner) {
            defaultBranchRef {
                target {
                    ... on Commit {
                        history(first: 100, after: $cursor) {
                            totalCount
                            edges {
                                node {
                                    ... on Commit {
                                        committedDate
                                    }
                                    author {
                                        user {
                                            id
                                        }
                                    }
                                    deletions
                                    additions
                                }
                            }
                            pageInfo {
                                endCursor
                                hasNextPage
                            }
                        }
                    }
                }
            }
        }
    }"""
    variables = {"repo_name": repo_name, "owner": owner, "cursor": cursor}
    # Issued directly (not via post_graphql) because an error here must first
    # persist the partial cache and distinguish the 403 anti-abuse limit.
    response = requests.post(
        config.GITHUB_GRAPHQL_URL,
        json={"query": query, "variables": variables},
        headers=config.API_HEADERS)
    if response.status_code == 200:
        branch = response.json()["data"]["repository"]["defaultBranchRef"]
        if branch is not None:
            history = branch["target"]["history"]
            return _accumulate_loc_page(
                owner, repo_name, cache_rows, cache_comment, history,
                additions, deletions, commits)
        return 0
    save_partial_cache(cache_rows, cache_comment)
    if response.status_code == 403:
        raise Exception(
            "Too many requests in a short amount of time!\n"
            "You've hit the non-documented anti-abuse limit!")
    raise Exception("fetch_repo_loc() has failed with a",
                    response.status_code, response.text, QUERY_COUNT)


def _accumulate_loc_page(owner, repo_name, cache_rows, cache_comment, history,
                         additions, deletions, commits):
    """Fold one page of commit history into the running totals.

    Only commits with a resolvable author user are counted. Recurses via
    :func:`fetch_repo_loc` when further history pages remain.

    :param str owner: Repository owner.
    :param str repo_name: Repository name.
    :param list cache_rows: In-memory cache rows (forwarded on recursion).
    :param list cache_comment: Comment header lines (forwarded on recursion).
    :param dict history: ``history`` node from the GraphQL response.
    :param int additions: Running addition total before this page.
    :param int deletions: Running deletion total before this page.
    :param int commits: Running commit count before this page.
    :return: Triple ``(additions, deletions, commits)``.
    :rtype: tuple
    """
    for edge in history["edges"]:
        if edge["node"]["author"]["user"] is not None:
            commits += 1
            additions += edge["node"]["additions"]
            deletions += edge["node"]["deletions"]
    if history["edges"] == [] or not history["pageInfo"]["hasNextPage"]:
        return additions, deletions, commits
    return fetch_repo_loc(owner, repo_name, cache_rows, cache_comment,
                          additions, deletions, commits,
                          history["pageInfo"]["endCursor"])


def build_loc_cache(owner_affiliations, comment_size=0, force_cache=False,
                    cursor=None, edges=None):
    """Page through every repository, then reconcile and total the cache.

    :param list owner_affiliations: Repository affiliation filters.
    :param int comment_size: Number of comment header lines in the cache file.
    :param bool force_cache: If ``True``, force a full cache rebuild.
    :param str cursor: Pagination cursor.
    :param list edges: Repository edges accumulated across pages.
    :return: List ``[additions, deletions, net_loc, was_cached]``.
    :rtype: list
    """
    if edges is None:
        edges = []
    increment_query_count("build_loc_cache")
    query = """
    query ($owner_affiliation: [RepositoryAffiliation], $login: String!,
           $cursor: String) {
        user(login: $login) {
            repositories(first: 60, after: $cursor,
                         ownerAffiliations: $owner_affiliation) {
                edges {
                    node {
                        ... on Repository {
                            nameWithOwner
                            defaultBranchRef {
                                target {
                                    ... on Commit {
                                        history {
                                            totalCount
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                pageInfo {
                    endCursor
                    hasNextPage
                }
            }
        }
    }"""
    variables = {"owner_affiliation": owner_affiliations,
                 "login": config.USER_NAME, "cursor": cursor}
    response = post_graphql("build_loc_cache", query, variables)
    repositories = response.json()["data"]["user"]["repositories"]
    if repositories["pageInfo"]["hasNextPage"]:
        edges += repositories["edges"]
        return build_loc_cache(owner_affiliations, comment_size, force_cache,
                               repositories["pageInfo"]["endCursor"], edges)
    return _reconcile_cache(edges + repositories["edges"],
                            comment_size, force_cache)


def _reconcile_cache(edges, comment_size, force_cache, loc_add=0, loc_del=0):
    """Sync the on-disk cache with current repository data and total the LOC.

    Creates the cache file if missing. When the repository set changed (or
    *force_cache* is set) the rows are reset first. Each repository whose
    commit count changed is re-fetched via :func:`fetch_repo_loc`.

    :param list edges: All repository edges from the repositories query.
    :param int comment_size: Number of comment header lines.
    :param bool force_cache: Force a full cache flush and rebuild.
    :param int loc_add: Accumulated additions (recursion accumulator).
    :param int loc_del: Accumulated deletions (recursion accumulator).
    :return: ``[total_additions, total_deletions, net_loc, was_cached]``.
    :rtype: list
    """
    was_cached = True
    filename = config.user_cache_path()
    try:
        with open(filename, "r") as f:
            cache_rows = f.readlines()
    except FileNotFoundError:
        cache_rows = []
        if comment_size > 0:
            for _ in range(comment_size):
                cache_rows.append(
                    "This line is a comment block. "
                    "Write whatever you want here.\n")
        with open(filename, "w") as f:
            f.writelines(cache_rows)

    # A mismatch between cached rows and current repos means the repo set
    # changed; wipe the data rows (keeping the comment header) and reload.
    if len(cache_rows) - comment_size != len(edges) or force_cache:
        was_cached = False
        _reset_cache_rows(edges, filename, comment_size)
        with open(filename, "r") as f:
            cache_rows = f.readlines()

    cache_comment = cache_rows[:comment_size]
    cache_rows = cache_rows[comment_size:]
    for index in range(len(edges)):
        cached_hash, cached_commits, *_rest = cache_rows[index].split()
        if cached_hash == _repo_hash(edges[index]["node"]["nameWithOwner"]):
            try:
                latest_commits = (edges[index]["node"]["defaultBranchRef"]
                                  ["target"]["history"]["totalCount"])
                if int(cached_commits) != latest_commits:
                    owner, repo_name = (
                        edges[index]["node"]["nameWithOwner"].split("/"))
                    loc = fetch_repo_loc(owner, repo_name,
                                         cache_rows, cache_comment)
                    cache_rows[index] = (
                        cached_hash + " " + str(latest_commits) + " " +
                        str(loc[2]) + " " + str(loc[0]) + " " +
                        str(loc[1]) + "\n")
            except TypeError:
                # No default branch / empty repo: record a zeroed row.
                cache_rows[index] = cached_hash + " 0 0 0 0\n"
    with open(filename, "w") as f:
        f.writelines(cache_comment)
        f.writelines(cache_rows)
    for row in cache_rows:
        columns = row.split()
        loc_add += int(columns[3])
        loc_del += int(columns[4])
    return [loc_add, loc_del, loc_add - loc_del, was_cached]


def _reset_cache_rows(edges, filename, comment_size):
    """Rewrite the cache with a zeroed row per repository, keeping the header.

    :param list edges: Repository edges to seed fresh zero-rows for.
    :param str filename: Path to the cache file.
    :param int comment_size: Number of comment header lines to preserve.
    """
    with open(filename, "r") as f:
        header = []
        if comment_size > 0:
            header = f.readlines()[:comment_size]
    with open(filename, "w") as f:
        f.writelines(header)
        for edge in edges:
            f.write(_repo_hash(edge["node"]["nameWithOwner"]) + " 0 0 0 0\n")


def save_partial_cache(cache_rows, cache_comment):
    """Persist whatever cache data exists so an error does not lose progress.

    :param list cache_rows: Cache data rows to write.
    :param list cache_comment: Comment header lines.
    """
    filename = config.user_cache_path()
    with open(filename, "w") as f:
        f.writelines(cache_comment)
        f.writelines(cache_rows)
    print("There was an error while writing to the cache file. The file,",
          filename, "has had the partial data saved and closed.")


def sum_cached_commits(comment_size):
    """Sum authored commits across every cached repository row.

    Rows are ``hash totalCount myCommits additions deletions``; this totals the
    third column (``myCommits``), not the branch-wide ``totalCount``.

    :param int comment_size: Number of comment header lines to skip.
    :return: Total authored-commit count across all cached repositories.
    :rtype: int
    :raises FileNotFoundError: If the cache file does not exist.
    """
    filename = config.user_cache_path()
    with open(filename, "r") as f:
        rows = f.readlines()[comment_size:]
    return sum(int(row.split()[2]) for row in rows)


def cached_loc_totals(comment_size):
    """Return the last cached LOC totals without contacting the API.

    Lets a tokenless or failed run reuse previously computed stats instead of
    zeroing the card.

    :param int comment_size: Number of comment header lines to skip.
    :return: List ``[additions, deletions, net_loc]``.
    :rtype: list
    """
    filename = config.user_cache_path()
    additions = deletions = 0
    try:
        with open(filename, "r") as f:
            rows = f.readlines()[comment_size:]
    except FileNotFoundError:
        return [0, 0, 0]
    for row in rows:
        columns = row.split()
        if len(columns) >= 5:
            additions += int(columns[3])
            deletions += int(columns[4])
    return [additions, deletions, additions - deletions]


def cached_commit_total(comment_size):
    """Return the cached commit total, or ``0`` when the cache is unusable.

    :param int comment_size: Number of comment header lines to skip.
    :return: Total cached commit count.
    :rtype: int
    """
    try:
        return sum_cached_commits(comment_size)
    except (FileNotFoundError, IndexError, ValueError):
        return 0
