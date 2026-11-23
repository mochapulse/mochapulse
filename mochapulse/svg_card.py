"""Build the SVG profile card and inject live stats into it.

The card has two panels inside one SVG: ASCII art on the left and a
neofetch-style info list on the right. Dynamic numbers are written as
placeholder zeros here (with stable ``id`` attributes) and overwritten later
by :func:`inject_stats`. All human-authored text is XML-escaped at render
time, so entry data may contain ``&``, ``<`` or ``>`` literally.
"""
from lxml import etree

from . import config

# Layout constants (pixels unless noted).
_ART_Y_START = 40
_ART_LINE_HEIGHT = 20
_ART_FONT_SIZE = 12
_ART_X_PADDING = 20
_CHAR_WIDTH_RATIO = 0.6  # approximate glyph width as a fraction of font size
_INFO_MIN_X = 490
_INFO_CONTENT_WIDTH = 420
_INFO_Y_START = 40
_INFO_LINE_HEIGHT = 28
_INFO_FONT_SIZE = 16


def escape_text(text):
    """Escape the three characters that are illegal in XML text content.

    ``&`` must be escaped first so the ``&`` introduced by escaping ``<``/``>``
    is not escaped again.

    :param str text: Raw text to place inside an SVG element.
    :return: XML-safe text.
    :rtype: str
    """
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))


def load_ascii_art():
    """Read the ASCII art file into a list of lines.

    :return: Art lines with trailing newlines removed.
    :rtype: list
    """
    with open(config.ASCII_ART_FILE) as f:
        return f.read().rstrip("\n").split("\n")


def _info_entries():
    """Return the static info-panel rows as ``(kind, label, value)`` tuples.

    ``kind`` selects how a row renders (see :func:`build_svg_document`). Text
    is stored raw; escaping happens at render time.

    :return: Ordered list of info-panel entry tuples.
    :rtype: list
    """
    return [
        ("title", "mochapulse@github", ""),
        ("subtitle", "AI agents · Embedded systems · RF & SDR", ""),
        ("uptime", "Uptime", ""),
        ("kv", "OS", "WSL, Linux (Debian, Pop!_OS, Arch Linux)"),
        ("kv", "Shell", "zsh, Oh My Zsh, bash, PowerShell"),
        ("kv", "Terminal", "Kitty, Windows Terminal"),
        ("kv", "Editor", "VS Code, Neovim, Nano"),
        ("kv", "Languages", "Python, C, C++, Node(TS or JS), Vite/React"),
        ("kv", "CI/CD", "GH Actions, Docker"),
        ("kv", "", "Embedded Systems (ESP32, RPI, Jetson Nano)"),
        ("blank", "", ""),
        ("sep", "AI Engineering", ""),
        ("kv", "Agents", "Custom agents & harnesses"),
        ("kv", "Methodology", "SDD and beyond — own code-dev workflows"),
        ("kv", "Stack", "Skills, MCP, Plugins, Local LLMs"),
        ("blank", "", ""),
        ("sep", "RF & Networking", ""),
        ("kv", "SDR", "Software-defined radio"),
        ("kv", "Networking", "Internet & wireless networks"),
        ("blank", "", ""),
        ("sep", "Repository", ""),
        ("kv", "mochapulse", "GitHub profile README"),
        ("kv", "as‑a‑service", "Mocha as a service"),
        ("blank", "", ""),
        ("sep", "Contact", ""),
        ("kv", "GitHub", "github.com/mochapulse"),
        ("kv", "Website", "mochapulse.github.io/mochapulse"),
        ("kv", "Gmail", "mochapulse@gmail.com"),
        ("kv", "LinkedIn", "linkedin.com/in/david-ramirez-betancourth-b5ba80279"),
        ("blank", "", ""),
        ("sep", "GitHub Stats", ""),
        ("stats_repos", "", ""),
        ("stats_commits", "", ""),
        ("stats_loc", "", ""),
    ]


def build_svg_document(ascii_lines, theme):
    """Render a complete SVG string for one color *theme*.

    :param list ascii_lines: ASCII art lines for the left panel.
    :param config.Theme theme: Colors for this variant (dark or light).
    :return: Complete SVG document.
    :rtype: str
    """
    max_art_chars = max((len(line.rstrip()) for line in ascii_lines),
                        default=0)
    art_pixel_width = int(max_art_chars * _ART_FONT_SIZE * _CHAR_WIDTH_RATIO)
    art_right_edge = _ART_X_PADDING + art_pixel_width
    info_x = max(_INFO_MIN_X, art_right_edge + 10)
    svg_width = max(config.SVG_MIN_WIDTH, info_x + _INFO_CONTENT_WIDTH)

    art_height = _ART_Y_START + len(ascii_lines) * _ART_LINE_HEIGHT + 20

    # Left panel: one <tspan> per art line.
    art_tspans = []
    for i, line in enumerate(ascii_lines):
        stripped = line.rstrip()
        y = _ART_Y_START + i * _ART_LINE_HEIGHT
        if stripped:
            art_tspans.append(
                f'      <tspan x="{_ART_X_PADDING}" y="{y}"'
                f' xml:space="preserve">{escape_text(stripped)}</tspan>')
        else:
            art_tspans.append(
                f'      <tspan x="{_ART_X_PADDING}" y="{y}"> </tspan>')

    entries = _info_entries()
    info_height = _INFO_Y_START + len(entries) * _INFO_LINE_HEIGHT + 20
    svg_height = max(art_height, info_height)

    # Right panel: render each entry according to its kind.
    info_tspans = []
    for i, (kind, label, value) in enumerate(entries):
        y = _INFO_Y_START + i * _INFO_LINE_HEIGHT
        if kind == "title":
            info_tspans.append(
                f'      <tspan x="{info_x}" y="{y}">'
                f'{escape_text(label)} {"—" * 40}</tspan>')
        elif kind == "subtitle":
            info_tspans.append(
                f'      <tspan x="{info_x}" y="{y}" class="value">'
                f'{escape_text(label)}</tspan>')
        elif kind == "uptime":
            info_tspans.append(
                f'      <tspan x="{info_x}" y="{y}">'
                f'<tspan class="key">{escape_text(label)}</tspan>'
                f'<tspan class="cc" id="age_data_dots">'
                f'{"." * 4} </tspan>'
                f'<tspan class="value" id="age_data">0</tspan>'
                f'</tspan>')
        elif kind == "kv":
            info_tspans.append(
                f'      <tspan x="{info_x}" y="{y}">'
                f'<tspan class="key">{escape_text(label)}</tspan>'
                f'<tspan class="cc">{"." * 4} </tspan>'
                f'<tspan class="value">{escape_text(value)}</tspan>'
                f'</tspan>')
        elif kind == "blank":
            info_tspans.append(
                f'      <tspan x="{info_x}" y="{y}"> </tspan>')
        elif kind == "sep":
            info_tspans.append(
                f'      <tspan x="{info_x}" y="{y}">'
                f'{escape_text(label)} {"—" * 40}</tspan>')
        elif kind == "stats_repos":
            info_tspans.append(
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
            info_tspans.append(
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
            info_tspans.append(
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

    return (
        f"<?xml version='1.0' encoding='UTF-8'?>\n"
        f'<svg xmlns="http://www.w3.org/2000/svg"\n'
        f'     font-family="ConsolasFallback,Consolas,monospace"\n'
        f'     width="{svg_width}px" height="{svg_height}px"'
        f' font-size="{_INFO_FONT_SIZE}px">\n'
        f'<style>\n'
        f'  @font-face {{\n'
        f"    src: local('Consolas'), local('Consolas Bold');\n"
        f"    font-family: 'ConsolasFallback';\n"
        f'    font-display: swap;\n'
        f'    -webkit-size-adjust: 109%;\n'
        f'    size-adjust: 109%;\n'
        f'  }}\n'
        f'  .key {{ fill: {theme.key}; }}\n'
        f'  .value {{ fill: {theme.value}; }}\n'
        f'  .cc {{ fill: {theme.neutral}; }}\n'
        f'  .addColor {{ fill: {theme.add}; }}\n'
        f'  .delColor {{ fill: {theme.del_}; }}\n'
        f'  text, tspan {{ white-space: pre; }}\n'
        f'</style>\n'
        f'<rect width="{svg_width}px" height="{svg_height}px"'
        f' fill="{theme.bg}" rx="15"/>\n'
        f'<text fill="{theme.fg}" font-size="{_ART_FONT_SIZE}px">\n'
        f'{chr(10).join(art_tspans)}\n'
        f'</text>\n'
        f'<text fill="{theme.fg}">\n'
        f'{chr(10).join(info_tspans)}\n'
        f'</text>\n'
        f'</svg>'
    )


def inject_stats(filename, age, commits, stars, repos, contributed,
                 followers, loc):
    """Parse an SVG file and replace placeholder values with live stats.

    :param str filename: Path to the SVG file to update in place.
    :param str age: Human-readable age string.
    :param int commits: Total authored-commit count.
    :param int stars: Total stargazer count.
    :param int repos: Owned-repository count.
    :param int contributed: Contributed-repository count.
    :param int followers: Follower count.
    :param list loc: ``[additions, deletions, net_loc]``.
    """
    tree = etree.parse(filename)
    root = tree.getroot()
    _set_padded_value(root, "age_data", age, 35)
    _set_padded_value(root, "commit_data", commits, 10)
    _set_padded_value(root, "star_data", stars, 8)
    _set_padded_value(root, "repo_data", repos, 4)
    _set_padded_value(root, "contrib_data", contributed)
    _set_padded_value(root, "follower_data", followers, 10)
    _set_padded_value(root, "loc_data", loc[2], 12)
    _set_padded_value(root, "loc_add", loc[0], 10)
    _set_padded_value(root, "loc_del", loc[1], 10)
    tree.write(filename, encoding="utf-8", xml_declaration=True)


def _set_padded_value(root, element_id, new_text, width=0):
    """Set an element's text and right-align it with dot padding.

    Thousands-separates integers, writes the value into ``<element_id>``, and
    fills the companion ``<element_id>_dots`` element so the value column lines
    up in the monospace layout.

    :param lxml.etree.Element root: Root of the SVG tree.
    :param str element_id: ``id`` of the value ``<tspan>``.
    :param new_text: Value to write (``int`` is formatted with commas).
    :type new_text: int or str
    :param int width: Target character width for alignment padding.
    """
    if isinstance(new_text, int):
        new_text = "{:,}".format(new_text)
    new_text = str(new_text)
    _set_element_text(root, element_id, new_text)
    pad_len = max(0, width - len(new_text))
    if pad_len <= 2:
        dot_string = {0: "", 1: " ", 2: ". "}[pad_len]
    else:
        dot_string = " " + ("." * pad_len) + " "
    _set_element_text(root, f"{element_id}_dots", dot_string)


def _set_element_text(root, element_id, new_text):
    """Replace the text of the SVG element with the given ``id``.

    :param lxml.etree.Element root: Root of the SVG tree.
    :param str element_id: ``id`` of the target element.
    :param str new_text: Replacement text.
    """
    element = root.find(f".//*[@id='{element_id}']")
    if element is not None:
        element.text = new_text
