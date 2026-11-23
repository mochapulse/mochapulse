"""Stateless GitHub GraphQL fetchers (no cache interaction).

Each function issues one category of query and returns plain Python values.
LOC/commit history lives in :mod:`mochapulse.loc_cache` because it is tightly
coupled to the on-disk cache; this module only depends on
:func:`post_graphql`, so there is no import cycle.
"""
import requests

from . import config
from .metrics import increment_query_count


def post_graphql(caller_name, query, variables):
    """Send one GraphQL request and return the successful response.

    :param str caller_name: Caller label used in the error message.
    :param str query: GraphQL query document.
    :param dict variables: GraphQL variables.
    :return: The successful ``requests.Response``.
    :rtype: requests.Response
    :raises Exception: If the HTTP status code is not 200.
    """
    response = requests.post(
        config.GITHUB_GRAPHQL_URL,
        json={"query": query, "variables": variables},
        headers=config.API_HEADERS)
    if response.status_code == 200:
        return response
    raise Exception(caller_name, " has failed with a", response.status_code,
                    response.text)


def _sum_stars(repository_edges):
    """Sum stargazer counts across a list of repository edges.

    :param list repository_edges: ``edges`` array from a repositories query.
    :return: Total stargazers across the repositories.
    :rtype: int
    """
    return sum(edge["node"]["stargazers"]["totalCount"]
               for edge in repository_edges)


def fetch_repos_or_stars(count_type, owner_affiliations, cursor=None):
    """Fetch either the owned-repository count or cumulative star count.

    Pages through all repositories using *cursor*.

    :param str count_type: ``"repos"`` for the repository count or
        ``"stars"`` for the cumulative stargazer count.
    :param list owner_affiliations: Affiliation filters, e.g. ``["OWNER"]``.
    :param str cursor: Pagination cursor for the next page.
    :return: Repository count or total stars, depending on *count_type*.
    :rtype: int
    """
    increment_query_count("fetch_repos_or_stars")
    query = """
    query ($owner_affiliation: [RepositoryAffiliation], $login: String!,
           $cursor: String) {
        user(login: $login) {
            repositories(first: 100, after: $cursor,
                         ownerAffiliations: $owner_affiliation) {
                totalCount
                edges {
                    node {
                        ... on Repository {
                            nameWithOwner
                            stargazers {
                                totalCount
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
    response = post_graphql("fetch_repos_or_stars", query, variables)
    repositories = response.json()["data"]["user"]["repositories"]
    if count_type == "repos":
        return repositories["totalCount"]
    elif count_type == "stars":
        return _sum_stars(repositories["edges"])


def fetch_user(username):
    """Fetch a user's GitHub node id and account creation date.

    :param str username: GitHub username.
    :return: Tuple ``({"id": <node_id>}, created_at_iso_string)``.
    :rtype: tuple
    """
    increment_query_count("fetch_user")
    query = """
    query($login: String!){
        user(login: $login) {
            id
            createdAt
        }
    }"""
    response = post_graphql("fetch_user", query, {"login": username})
    user = response.json()["data"]["user"]
    return {"id": user["id"]}, user["createdAt"]


def fetch_follower_count(username):
    """Fetch the total number of followers for a user.

    :param str username: GitHub username.
    :return: Follower count.
    :rtype: int
    """
    increment_query_count("fetch_follower_count")
    query = """
    query($login: String!){
        user(login: $login) {
            followers {
                totalCount
            }
        }
    }"""
    response = post_graphql("fetch_follower_count", query, {"login": username})
    return int(response.json()["data"]["user"]["followers"]["totalCount"])
