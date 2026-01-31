from __future__ import annotations

import requests
from typing import Optional
import base64

def _strip_inline_comment(s: str) -> str:
    """
    Remove inline comments that start with #, but only when # is not inside quotes.
    """
    in_single = False
    in_double = False
    for i, ch in enumerate(s):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            return s[:i].rstrip()
    return s.rstrip()


def _unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and ((s[0] == s[-1] == '"') or (s[0] == s[-1] == "'")):
        return s[1:-1]
    return s


def parse_language_type_and_color(yml_text: str) -> dict[str, dict[str, Optional[str]]]:
    """
    Returns: {language_name: {"type": <str|None>, "color": <str|None>}, ...}
    """
    languages: dict[str, dict[str, Optional[str]]] = {}

    current_lang: Optional[str] = None

    for raw_line in yml_text.splitlines():
        line = raw_line.rstrip("\n")

        # Skip YAML document marker and empty lines
        stripped = line.strip()
        if not stripped or stripped == "---":
            continue

        # Skip full-line comments (allow leading spaces)
        if stripped.startswith("#"):
            continue

        # Top-level key: "Language Name:"
        if line and not line[0].isspace() and stripped.endswith(":"):
            lang_name = stripped[:-1].strip()
            current_lang = lang_name
            languages.setdefault(current_lang, {"type": None, "color": None})
            continue

        # If we're not inside a language block, ignore
        if current_lang is None:
            continue

        # We only care about fields at indentation level 2: "  type: ..." / "  color: ..."
        if line.startswith("  ") and not line.startswith("    "):
            no_comment = _strip_inline_comment(line.strip())
            if ":" not in no_comment:
                continue

            key, value = no_comment.split(":", 1)
            key = key.strip()
            value = _unquote(value.strip()) if value.strip() else ""

            if key == "type":
                languages[current_lang]["type"] = value or None
            elif key == "color":
                languages[current_lang]["color"] = value or None

    return languages


def _get_language_colors(yml_file_data: str) -> dict[str, str | None]:
    parsed = parse_language_type_and_color(yml_file_data)

    out: dict[str, Optional[str]] = {}
    for lang_name, attrs in parsed.items():
        if attrs.get("type") != "programming":
            continue

        color = attrs.get("color")
        if color is None:
            continue

        out[lang_name] = color
    return out


def get_language_color_map(headers: dict[str, str]):
    linguist_yml = requests.get(
        url="https://api.github.com/repos/github-linguist/linguist/contents/lib/linguist/languages.yml",
        headers=headers,
    )
    linguist_yml.raise_for_status()
    return _get_language_colors(base64.b64decode(linguist_yml.json()["content"]).decode("utf-8"))