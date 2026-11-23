"""Lightweight instrumentation: API-call accounting and wall-clock timing.

``QUERY_COUNT`` is a process-wide tally of GraphQL calls by category. It is a
single shared dict object, so any module that imports it and mutates it via
:func:`increment_query_count` updates the same counters the summary reads.
"""
import time

# One counter per category of GraphQL request. Keys mirror the fetcher that
# owns each category so the end-of-run summary is self-explanatory.
QUERY_COUNT = {
    "fetch_user": 0,
    "fetch_follower_count": 0,
    "fetch_repos_or_stars": 0,
    "fetch_repo_loc": 0,
    "build_loc_cache": 0,
}


def increment_query_count(category):
    """Increment the GraphQL call counter for *category*.

    :param str category: Key in :data:`QUERY_COUNT` to increment.
    """
    QUERY_COUNT[category] += 1


def time_call(func, *args):
    """Invoke *func* with *args* and measure its wall-clock duration.

    :param callable func: Function to execute and time.
    :param args: Positional arguments forwarded to *func*.
    :return: Tuple ``(return_value, elapsed_seconds)``.
    :rtype: tuple
    """
    start = time.perf_counter()
    result = func(*args)
    return result, time.perf_counter() - start


def print_timing(label, seconds):
    """Print a single aligned timing line to stdout.

    Durations of at least one second are shown in seconds; shorter ones in
    milliseconds.

    :param str label: Human-readable label for the measured step.
    :param float seconds: Elapsed time in seconds.
    """
    print("{:<23}".format("   " + label + ":"), sep="", end="")
    if seconds > 1:
        print("{:>12}".format("%.4f" % seconds + " s "))
    else:
        print("{:>12}".format("%.4f" % (seconds * 1000) + " ms"))
