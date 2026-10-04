#!/usr/bin/env python3
"""Render the plugin table and dependency diagram into README.md from plugins.json and the catalog.

plugins.json lists every ihav plugin, public or private. `depends_on` holds dependencies declared in a plugin's
manifest (solid arrows); `uses` holds runtime or contract links that are not declared (dashed arrows). The catalog
column comes from .claude-plugin/marketplace.json. `--check` exits 1 when README.md is out of date.
"""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
BEGIN, END = "<!-- plugins:begin -->", "<!-- plugins:end -->"


def node(name):
    return name.replace("-", "_")


def label(text):
    """Quote a Mermaid label; parentheses and brackets inside an unquoted label break the parser."""
    return '"' + text.replace('"', "#quot;") + '"'


def render():
    registry = json.loads((ROOT / "plugins.json").read_text(encoding="utf-8"))["plugins"]
    catalog = {p["name"]: p["source"] for p in json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))["plugins"]}
    names = {p["name"] for p in registry}
    missing = sorted(set(catalog) - names)
    if missing:
        raise SystemExit(f"plugins.json lacks catalog plugins: {missing}")
    rows = ["| Plugin | Repository | In this catalog | What it does |", "|---|---|---|---|"]
    lines = ["```mermaid", "flowchart LR"]
    for p in sorted(registry, key=lambda p: (p["visibility"] != "public", p["name"])):
        url = f"https://github.com/hiendang7613/{p['name']}"
        source = catalog.get(p["name"])
        pinned = source.get("ref", "main") if isinstance(source, dict) else ("yes" if source else "no")
        rows.append(f"| [{p['name']}]({url}) | {p['visibility']} | {pinned if source else 'no'} | {p['description']} |")
        shape = (f'{node(p["name"])}[{label(p["name"])}]' if p["visibility"] == "public"
                 else f'{node(p["name"])}({label(p["name"] + " (private)")})')
        lines.append(f"  {shape}")
    for p in registry:
        for target in p["depends_on"]:
            if target not in names:
                raise SystemExit(f"{p['name']} depends on unknown plugin {target}")
            lines.append(f"  {node(p['name'])} -->|{label('declared')}| {node(target)}")
        for use in p["uses"]:
            if use["name"] not in names:
                raise SystemExit(f"{p['name']} uses unknown plugin {use['name']}")
            lines.append(f"  {node(p['name'])} -.->|{label(use['why'])}| {node(use['name'])}")
    lines.append("```")
    legend = ("Solid arrows are dependencies declared in a plugin's manifest; the host installs them together. "
              "Dashed arrows are runtime or contract links that are not declared. Rounded boxes are private repositories.")
    return "\n".join([BEGIN, "", *rows, "", *lines, "", legend, "", END])


def main():
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    start, end = text.index(BEGIN), text.index(END) + len(END)
    updated = text[:start] + render() + text[end:]
    if "--check" in sys.argv:
        if updated != text:
            print("::error::README.md plugin map is out of date; run python3 scripts/render_readme.py")
            return 1
        return 0
    readme.write_text(updated, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
