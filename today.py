import datetime
from dateutil import relativedelta
import hashlib
import os
import sys
import time
import requests
from lxml import etree

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASCII_FILE = os.path.join(SCRIPT_DIR, "mochapulse-ascii-art.txt")

ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', '')
USER_NAME = os.environ.get('USER_NAME', 'mochapulse')
HEADERS = {'authorization': 'token ' + ACCESS_TOKEN} if ACCESS_TOKEN else {}
HAS_TOKEN = bool(ACCESS_TOKEN)
BIRTHDAY = datetime.datetime(2001, 6, 28)
QUERY_COUNT = {'user_getter': 0, 'follower_getter': 0, 'graph_repos_stars': 0,
               'recursive_loc': 0, 'loc_query': 0}

SVG_WIDTH = 1160

DARK_BG = "#0d1117"
DARK_FG = "#c9d1d9"
DARK_KEY = "#ffa657"
DARK_VALUE = "#a5d6ff"
DARK_NEUTRAL = "#555d66"
DARK_ADD = "#3fb950"
DARK_DEL = "#f85149"

LIGHT_BG = "#f6f8fa"
LIGHT_FG = "#24292f"
LIGHT_KEY = "#953800"
LIGHT_VALUE = "#0a3069"
LIGHT_NEUTRAL = "#c0c8d4"
LIGHT_ADD = "#1a7f37"
LIGHT_DEL = "#cf222e"


def daily_readme(birthday):
    diff = relativedelta.relativedelta(datetime.datetime.today(), birthday)
    return '{} {}, {} {}, {} {}{}'.format(
        diff.years, 'year' + _plural(diff.years),
        diff.months, 'month' + _plural(diff.months),
        diff.days, 'day' + _plural(diff.days),
        ' 🎂' if (diff.months == 0 and diff.days == 0) else '')


def _plural(unit):
    return 's' if unit != 1 else ''


def simple_request(func_name, query, variables):
    request = requests.post('https://api.github.com/graphql',
                            json={'query': query, 'variables': variables},
                            headers=HEADERS)
    if request.status_code == 200:
        return request
    raise Exception(func_name, ' has failed with a', request.status_code,
                    request.text, QUERY_COUNT)


def graph_repos_stars(count_type, owner_affiliation, cursor=None):
    query_count('graph_repos_stars')
    query = '''
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
    }'''
    variables = {'owner_affiliation': owner_affiliation, 'login': USER_NAME,
                 'cursor': cursor}
    request = simple_request(graph_repos_stars.__name__, query, variables)
    if count_type == 'repos':
        return request.json()['data']['user']['repositories']['totalCount']
    elif count_type == 'stars':
        return _stars_counter(
            request.json()['data']['user']['repositories']['edges'])


def recursive_loc(owner, repo_name, data, cache_comment, addition_total=0,
                  deletion_total=0, my_commits=0, cursor=None):
    query_count('recursive_loc')
    query = '''
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
    }'''
    variables = {'repo_name': repo_name, 'owner': owner, 'cursor': cursor}
    request = requests.post('https://api.github.com/graphql',
                            json={'query': query, 'variables': variables},
                            headers=HEADERS)
    if request.status_code == 200:
        if request.json()['data']['repository']['defaultBranchRef'] is not None:
            return _loc_counter_one_repo(
                owner, repo_name, data, cache_comment,
                request.json()['data']['repository']['defaultBranchRef']['target']['history'],
                addition_total, deletion_total, my_commits)
        else:
            return 0
    force_close_file(data, cache_comment)
    if request.status_code == 403:
        raise Exception(
            'Too many requests in a short amount of time!\n'
            'You\'ve hit the non-documented anti-abuse limit!')
    raise Exception('recursive_loc() has failed with a',
                    request.status_code, request.text, QUERY_COUNT)


def _loc_counter_one_repo(owner, repo_name, data, cache_comment, history,
                          addition_total, deletion_total, my_commits):
    for node in history['edges']:
        if node['node']['author']['user'] is not None:
            my_commits += 1
            addition_total += node['node']['additions']
            deletion_total += node['node']['deletions']
    if history['edges'] == [] or not history['pageInfo']['hasNextPage']:
        return addition_total, deletion_total, my_commits
    else:
        return recursive_loc(owner, repo_name, data, cache_comment,
                             addition_total, deletion_total, my_commits,
                             history['pageInfo']['endCursor'])


def loc_query(owner_affiliation, comment_size=0, force_cache=False,
              cursor=None, edges=None):
    if edges is None:
        edges = []
    query_count('loc_query')
    query = '''
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
    }'''
    variables = {'owner_affiliation': owner_affiliation, 'login': USER_NAME,
                 'cursor': cursor}
    request = simple_request(loc_query.__name__, query, variables)
    if request.json()['data']['user']['repositories']['pageInfo']['hasNextPage']:
        edges += request.json()['data']['user']['repositories']['edges']
        return loc_query(owner_affiliation, comment_size, force_cache,
                         request.json()['data']['user']['repositories']['pageInfo']['endCursor'],
                         edges)
    else:
        return _cache_builder(
            edges + request.json()['data']['user']['repositories']['edges'],
            comment_size, force_cache)


def _cache_builder(edges, comment_size, force_cache, loc_add=0, loc_del=0):
    cached = True
    filename = 'cache/' + hashlib.sha256(
        USER_NAME.encode('utf-8')).hexdigest() + '.txt'
    try:
        with open(filename, 'r') as f:
            data = f.readlines()
    except FileNotFoundError:
        data = []
        if comment_size > 0:
            for _ in range(comment_size):
                data.append(
                    'This line is a comment block. '
                    'Write whatever you want here.\n')
        with open(filename, 'w') as f:
            f.writelines(data)

    if len(data) - comment_size != len(edges) or force_cache:
        cached = False
        _flush_cache(edges, filename, comment_size)
        with open(filename, 'r') as f:
            data = f.readlines()

    cache_comment = data[:comment_size]
    data = data[comment_size:]
    for index in range(len(edges)):
        repo_hash, commit_count, *__ = data[index].split()
        if repo_hash == hashlib.sha256(
                edges[index]['node']['nameWithOwner'].encode('utf-8')).hexdigest():
            try:
                if int(commit_count) != edges[index]['node']['defaultBranchRef']['target']['history']['totalCount']:
                    owner, repo_name = edges[index]['node']['nameWithOwner'].split('/')
                    loc = recursive_loc(owner, repo_name, data, cache_comment)
                    data[index] = (
                        repo_hash + ' ' +
                        str(edges[index]['node']['defaultBranchRef']['target']['history']['totalCount']) +
                        ' ' + str(loc[2]) + ' ' + str(loc[0]) + ' ' +
                        str(loc[1]) + '\n')
            except TypeError:
                data[index] = repo_hash + ' 0 0 0 0\n'
    with open(filename, 'w') as f:
        f.writelines(cache_comment)
        f.writelines(data)
    for line in data:
        loc = line.split()
        loc_add += int(loc[3])
        loc_del += int(loc[4])
    return [loc_add, loc_del, loc_add - loc_del, cached]


def _flush_cache(edges, filename, comment_size):
    with open(filename, 'r') as f:
        data = []
        if comment_size > 0:
            data = f.readlines()[:comment_size]
    with open(filename, 'w') as f:
        f.writelines(data)
        for node in edges:
            f.write(hashlib.sha256(
                node['node']['nameWithOwner'].encode('utf-8')).hexdigest() +
                ' 0 0 0 0\n')


def force_close_file(data, cache_comment):
    filename = 'cache/' + hashlib.sha256(
        USER_NAME.encode('utf-8')).hexdigest() + '.txt'
    with open(filename, 'w') as f:
        f.writelines(cache_comment)
        f.writelines(data)
    print('There was an error while writing to the cache file. The file,',
          filename, 'has had the partial data saved and closed.')


def _stars_counter(data):
    total_stars = 0
    for node in data:
        total_stars += node['node']['stargazers']['totalCount']
    return total_stars


def svg_overwrite(filename, age_data, commit_data, star_data, repo_data,
                  contrib_data, follower_data, loc_data):
    tree = etree.parse(filename)
    root = tree.getroot()
    _justify_format(root, 'age_data', age_data, 35)
    _justify_format(root, 'commit_data', commit_data, 10)
    _justify_format(root, 'star_data', star_data, 8)
    _justify_format(root, 'repo_data', repo_data, 4)
    _justify_format(root, 'contrib_data', contrib_data)
    _justify_format(root, 'follower_data', follower_data, 10)
    _justify_format(root, 'loc_data', loc_data[2], 12)
    _justify_format(root, 'loc_add', loc_data[0], 10)
    _justify_format(root, 'loc_del', loc_data[1], 10)
    tree.write(filename, encoding='utf-8', xml_declaration=True)


def _justify_format(root, element_id, new_text, length=0):
    if isinstance(new_text, int):
        new_text = f"{'{:,}'.format(new_text)}"
    new_text = str(new_text)
    _find_and_replace(root, element_id, new_text)
    just_len = max(0, length - len(new_text))
    if just_len <= 2:
        dot_map = {0: '', 1: ' ', 2: '. '}
        dot_string = dot_map[just_len]
    else:
        dot_string = ' ' + ('.' * just_len) + ' '
    _find_and_replace(root, f"{element_id}_dots", dot_string)


def _find_and_replace(root, element_id, new_text):
    element = root.find(f".//*[@id='{element_id}']")
    if element is not None:
        element.text = new_text


def commit_counter(comment_size):
    total_commits = 0
    filename = 'cache/' + hashlib.sha256(
        USER_NAME.encode('utf-8')).hexdigest() + '.txt'
    with open(filename, 'r') as f:
        data = f.readlines()
    data = data[comment_size:]
    for line in data:
        total_commits += int(line.split()[2])
    return total_commits


def user_getter(username):
    query_count('user_getter')
    query = '''
    query($login: String!){
        user(login: $login) {
            id
            createdAt
        }
    }'''
    variables = {'login': username}
    request = simple_request(user_getter.__name__, query, variables)
    return {'id': request.json()['data']['user']['id']}, \
        request.json()['data']['user']['createdAt']


def follower_getter(username):
    query_count('follower_getter')
    query = '''
    query($login: String!){
        user(login: $login) {
            followers {
                totalCount
            }
        }
    }'''
    request = simple_request(follower_getter.__name__, query,
                             {'login': username})
    return int(request.json()['data']['user']['followers']['totalCount'])


def query_count(funct_id):
    global QUERY_COUNT
    QUERY_COUNT[funct_id] += 1


def perf_counter(funct, *args):
    start = time.perf_counter()
    funct_return = funct(*args)
    return funct_return, time.perf_counter() - start


def formatter(query_type, difference, funct_return=False, whitespace=0):
    print('{:<23}'.format('   ' + query_type + ':'), sep='', end='')
    if difference > 1:
        print('{:>12}'.format('%.4f' % difference + ' s '))
    else:
        print('{:>12}'.format('%.4f' % (difference * 1000) + ' ms'))
    if whitespace:
        return f"{'{:,}'.format(funct_return): <{whitespace}}"
    return funct_return


def _load_ascii():
    with open(ASCII_FILE) as f:
        return f.read().rstrip("\n").split("\n")


def _build_svg(ascii_lines, bg, fg, key_color, value_color, neutral_color,
               add_color, del_color):
    art_y_start = 40
    art_line_height = 20
    art_font_size = 12

    info_x = 740
    info_y_start = 40
    info_line_height = 28
    info_font_size = 16

    art_height = art_y_start + len(ascii_lines) * art_line_height + 20

    tspans_art = []
    for i, line in enumerate(ascii_lines):
        rline = line.rstrip()
        y = art_y_start + i * art_line_height
        if rline:
            tspans_art.append(
                f'      <tspan x="20" y="{y}"'
                f' xml:space="preserve">{rline}</tspan>')
        else:
            tspans_art.append(f'      <tspan x="20" y="{y}"> </tspan>')

    info_entries = [
        ("title", "mochapulse@github", ""),
        ("uptime", "Uptime", ""),
        ("kv", "OS", "WSL, Linux(Debian, popOS, ArchLinux)"),
        ("kv", "Shell", "zsh, oh my zsh"),
        ("kv", "Terminal", "Kitty or Windows Terminal"),
        ("kv", "Editor", "VsCode"),
        ("kv", "Languages", "Python, C, C++, Node(TS or JS), Vite/React"),
        ("kv", "CI/CD",
         "GH Actions, Docker, Embedded Systems (ESP32, RPI, Jetson Nano)"),
        ("kv", "Tools", "Agents coding (Skills, Local LLMs)"),
        ("blank", "", ""),
        ("blank", "", ""),
        ("sep", "Repository", ""),
        ("kv", "mochapulse", "GitHub profile README"),
        ("kv", "as‑a‑service", "Mocha as a service"),
        ("blank", "", ""),
        ("sep", "Contact", ""),
        ("kv", "GitHub", "github.com/mochapulse"),
        ("blank", "", ""),
        ("sep", "GitHub Stats", ""),
        ("stats_repos", "", ""),
        ("stats_commits", "", ""),
        ("stats_loc", "", ""),
    ]

    info_height = info_y_start + len(info_entries) * info_line_height + 20
    svg_height = max(art_height, info_height)

    tspans_info = []
    for i, entry in enumerate(info_entries):
        y = info_y_start + i * info_line_height
        kind = entry[0]
        if kind == "title":
            k = entry[1]
            tspans_info.append(
                f'      <tspan x="{info_x}" y="{y}">'
                f'{k} {"—" * 40}</tspan>')
        elif kind == "uptime":
            k = entry[1]
            tspans_info.append(
                f'      <tspan x="{info_x}" y="{y}">'
                f'<tspan class="key">{k}</tspan>'
                f'<tspan class="cc" id="age_data_dots">'
                f'{"." * 4} </tspan>'
                f'<tspan class="value" id="age_data">0</tspan>'
                f'</tspan>')
        elif kind == "kv":
            k, v = entry[1], entry[2]
            tspans_info.append(
                f'      <tspan x="{info_x}" y="{y}">'
                f'<tspan class="key">{k}</tspan>'
                f'<tspan class="cc">{"." * 4} </tspan>'
                f'<tspan class="value">{v}</tspan>'
                f'</tspan>')
        elif kind == "blank":
            tspans_info.append(
                f'      <tspan x="{info_x}" y="{y}"> </tspan>')
        elif kind == "sep":
            k = entry[1]
            tspans_info.append(
                f'      <tspan x="{info_x}" y="{y}">'
                f'{k} {"—" * 40}</tspan>')
        elif kind == "stats_repos":
            tspans_info.append(
                f'      <tspan x="{info_x}" y="{y}">'
                f'<tspan class="key">Repos</tspan>'
                f'<tspan class="cc" id="repo_data_dots">'
                f'{"." * 4} </tspan>'
                f'<tspan class="value" id="repo_data">0</tspan>'
                f' {{<tspan class="key">Contributed</tspan>: '
                f'<tspan class="value" id="contrib_data">0</tspan>}}'
                f' | <tspan class="key">Stars</tspan>'
                f'<tspan class="cc" id="star_data_dots">'
                f'{"." * 4} </tspan>'
                f'<tspan class="value" id="star_data">0</tspan>'
                f'</tspan>')
        elif kind == "stats_commits":
            tspans_info.append(
                f'      <tspan x="{info_x}" y="{y}">'
                f'<tspan class="key">Commits</tspan>'
                f'<tspan class="cc" id="commit_data_dots">'
                f'{"." * 4} </tspan>'
                f'<tspan class="value" id="commit_data">0</tspan>'
                f' | <tspan class="key">Followers</tspan>'
                f'<tspan class="cc" id="follower_data_dots">'
                f'{"." * 4} </tspan>'
                f'<tspan class="value" id="follower_data">0</tspan>'
                f'</tspan>')
        elif kind == "stats_loc":
            tspans_info.append(
                f'      <tspan x="{info_x}" y="{y}">'
                f'<tspan class="key">Lines of Code on GitHub</tspan>'
                f'<tspan class="cc" id="loc_data_dots">'
                f'{"." * 4} </tspan>'
                f'<tspan class="value" id="loc_data">0</tspan>'
                f' ( <tspan class="addColor" id="loc_add">0</tspan>'
                f'<tspan class="addColor">++</tspan>'
                f', <tspan class="cc" id="loc_del_dots"> </tspan>'
                f'<tspan class="delColor" id="loc_del">0</tspan>'
                f'<tspan class="delColor">--</tspan> )'
                f'</tspan>')

    svg = (
        f"<?xml version='1.0' encoding='UTF-8'?>\n"
        f'<svg xmlns="http://www.w3.org/2000/svg"\n'
        f'     font-family="ConsolasFallback,Consolas,monospace"\n'
        f'     width="{SVG_WIDTH}px" height="{svg_height}px"'
        f' font-size="{info_font_size}px">\n'
        f'<style>\n'
        f'  @font-face {{\n'
        f"    src: local('Consolas'), local('Consolas Bold');\n"
        f"    font-family: 'ConsolasFallback';\n"
        f'    font-display: swap;\n'
        f'    -webkit-size-adjust: 109%;\n'
        f'    size-adjust: 109%;\n'
        f'  }}\n'
        f'  .key {{ fill: {key_color}; }}\n'
        f'  .value {{ fill: {value_color}; }}\n'
        f'  .cc {{ fill: {neutral_color}; }}\n'
        f'  .addColor {{ fill: {add_color}; }}\n'
        f'  .delColor {{ fill: {del_color}; }}\n'
        f'  text, tspan {{ white-space: pre; }}\n'
        f'</style>\n'
        f'<rect width="{SVG_WIDTH}px" height="{svg_height}px"'
        f' fill="{bg}" rx="15"/>\n'
        f'<text fill="{fg}" font-size="{art_font_size}px">\n'
        f'{chr(10).join(tspans_art)}\n'
        f'</text>\n'
        f'<text fill="{fg}">\n'
        f'{chr(10).join(tspans_info)}\n'
        f'</text>\n'
        f'</svg>'
    )
    return svg


def main():
    print('Calculation times:')

    ascii_lines = _load_ascii()
    sys.stdout.write(f"Loaded {len(ascii_lines)} ascii lines\n")

    dark = _build_svg(ascii_lines, DARK_BG, DARK_FG, DARK_KEY, DARK_VALUE,
                      DARK_NEUTRAL, DARK_ADD, DARK_DEL)
    with open(os.path.join(SCRIPT_DIR, "dark_mode.svg"), "w") as f:
        f.write(dark)
    sys.stdout.write("Wrote dark_mode.svg\n")

    light = _build_svg(ascii_lines, LIGHT_BG, LIGHT_FG, LIGHT_KEY,
                       LIGHT_VALUE, LIGHT_NEUTRAL, LIGHT_ADD, LIGHT_DEL)
    with open(os.path.join(SCRIPT_DIR, "light_mode.svg"), "w") as f:
        f.write(light)
    sys.stdout.write("Wrote light_mode.svg\n")

    age_data, age_time = perf_counter(daily_readme, BIRTHDAY)
    formatter('age calculation', age_time)

    if not HAS_TOKEN:
        print('\n** No ACCESS_TOKEN configured. Skipping GitHub API queries. **')
        print('** Set ACCESS_TOKEN and USER_NAME secrets in repo settings. **\n')
        svg_overwrite(os.path.join(SCRIPT_DIR, 'dark_mode.svg'),
                      age_data, 0, 0, 0, 0, 0, [0, 0, 0])
        svg_overwrite(os.path.join(SCRIPT_DIR, 'light_mode.svg'),
                      age_data, 0, 0, 0, 0, 0, [0, 0, 0])
        return

    try:
        user_data, user_time = perf_counter(user_getter, USER_NAME)
        OWNER_ID, acc_date = user_data
        formatter('account data', user_time)

        total_loc, loc_time = perf_counter(
            loc_query, ['OWNER', 'COLLABORATOR', 'ORGANIZATION_MEMBER'], 7)
        if total_loc[-1]:
            formatter('LOC (cached)', loc_time)
        else:
            formatter('LOC (no cache)', loc_time)

        commit_data, commit_time = perf_counter(commit_counter, 7)
        formatter('commits', commit_time)

        star_data, star_time = perf_counter(
            graph_repos_stars, 'stars', ['OWNER'])
        formatter('stars', star_time)

        repo_data, repo_time = perf_counter(
            graph_repos_stars, 'repos', ['OWNER'])
        formatter('repos', repo_time)

        contrib_data, contrib_time = perf_counter(
            graph_repos_stars, 'repos',
            ['OWNER', 'COLLABORATOR', 'ORGANIZATION_MEMBER'])
        formatter('contributed repos', contrib_time)

        follower_data, follower_time = perf_counter(
            follower_getter, USER_NAME)
        formatter('followers', follower_time)

        for index in range(len(total_loc) - 1):
            total_loc[index] = '{:,}'.format(total_loc[index])

        svg_overwrite(os.path.join(SCRIPT_DIR, 'dark_mode.svg'),
                      age_data, commit_data, star_data, repo_data,
                      contrib_data, follower_data, total_loc[:-1])
        svg_overwrite(os.path.join(SCRIPT_DIR, 'light_mode.svg'),
                      age_data, commit_data, star_data, repo_data,
                      contrib_data, follower_data, total_loc[:-1])

        print('Total GitHub GraphQL API calls:',
              '{:>3}'.format(sum(QUERY_COUNT.values())))
        for funct_name, count in QUERY_COUNT.items():
            print('{:<28}'.format('   ' + funct_name + ':'),
                  '{:>6}'.format(count))
    except Exception as e:
        print(f'\n** GitHub API error: {e} **')
        print('** SVG generated with placeholder stats. **\n')
        svg_overwrite(os.path.join(SCRIPT_DIR, 'dark_mode.svg'),
                      age_data, 0, 0, 0, 0, 0, [0, 0, 0])
        svg_overwrite(os.path.join(SCRIPT_DIR, 'light_mode.svg'),
                      age_data, 0, 0, 0, 0, 0, [0, 0, 0])


if __name__ == '__main__':
    main()
