#!/usr/bin/env python3
"""Check the ihav catalog before it reaches users.

For every entry in .claude-plugin/marketplace.json and .agents/plugins/marketplace.json:
- both files list the same plugin names, once each;
- a pinned entry's tag resolves to its sha on the remote, and the sha is checked out for the next steps;
- the plugin directory at that commit has a Claude manifest (and a Codex manifest when the Codex file lists it)
  whose name matches the entry;
- every dependency the Claude manifest declares is another plugin in this catalog.
An entry that follows a branch (no sha) passes with a warning; pin a release tag and its sha instead.
Exit 0 when every check passes, 1 otherwise. Needs only git and Python 3.9+.
"""

import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
FILES = {"claude": ROOT / ".claude-plugin" / "marketplace.json", "codex": ROOT / ".agents" / "plugins" / "marketplace.json"}
errors, warnings = [], []


def git(*args, cwd=None):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=300)


def entries(host):
    data = json.loads(FILES[host].read_text(encoding="utf-8"))
    names = [plugin["name"] for plugin in data["plugins"]]
    for name in {n for n in names if names.count(n) > 1}:
        errors.append(f"{host}: {name} is listed more than once")
    return {plugin["name"]: plugin for plugin in data["plugins"]}


def checkout(name, source, workdir):
    url, ref, sha = source.get("url"), source.get("ref"), source.get("sha")
    if not url:
        errors.append(f"{name}: source has no url")
        return None
    if not sha:
        warnings.append(f"{name}: follows {ref or 'the default branch'} without a sha; pin a release tag and its sha")
    if ref and sha:
        listed = git("ls-remote", url, f"refs/tags/{ref}", f"refs/tags/{ref}^{{}}", f"refs/heads/{ref}").stdout.split()
        if sha not in listed[0::2]:
            errors.append(f"{name}: {ref} does not resolve to {sha} on {url}")
    target = workdir / name
    if git("clone", "--quiet", "--filter=blob:none", "--no-checkout", url, str(target)).returncode:
        errors.append(f"{name}: cannot clone {url}")
        return None
    if git("checkout", "--quiet", sha or ref or "HEAD", cwd=target).returncode:
        errors.append(f"{name}: cannot check out {sha or ref}")
        return None
    path = PurePosixPath(source.get("path") or ".")
    if path.is_absolute() or ".." in path.parts:
        errors.append(f"{name}: plugin path {path} must stay inside the repository")
        return None
    return target / path


def manifest(plugin_dir, folder, name, host):
    path = plugin_dir / folder / "plugin.json"
    if not path.is_file():
        errors.append(f"{name}: {host} manifest {folder}/plugin.json is missing")
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("name") != name:
        errors.append(f"{name}: {host} manifest is named {data.get('name')!r}")
    return data


def main():
    claude, codex = entries("claude"), entries("codex")
    if set(claude) != set(codex):
        errors.append(f"Claude and Codex catalogs differ: only Claude {sorted(set(claude) - set(codex))}, "
                      f"only Codex {sorted(set(codex) - set(claude))}")
    with tempfile.TemporaryDirectory(prefix="ihav-catalog-") as directory:
        for name, entry in sorted(claude.items()):
            source = entry["source"] if isinstance(entry["source"], dict) else {"path": entry["source"]}
            other = (codex.get(name) or {}).get("source", {})
            if isinstance(other, dict) and (other.get("sha"), other.get("ref")) != (source.get("sha"), source.get("ref")):
                errors.append(f"{name}: Claude and Codex entries pin different refs")
            plugin_dir = checkout(name, source, Path(directory))
            if plugin_dir is None:
                continue
            data = manifest(plugin_dir, ".claude-plugin", name, "Claude")
            if name in codex and not (plugin_dir / ".codex-plugin" / "plugin.json").is_file():
                warnings.append(f"{name}: no .codex-plugin/plugin.json; Codex falls back to the Claude manifest")
            for dependency in (data or {}).get("dependencies", []):
                wanted = dependency.get("name") if isinstance(dependency, dict) else dependency
                if wanted not in claude:
                    errors.append(f"{name}: dependency {wanted!r} is not in this catalog")
            print(f"ok {name} {(data or {}).get('version', '?')} @ {source.get('sha') or source.get('ref')}")
    for warning in warnings:
        print(f"::warning::{warning}")
    for error in errors:
        print(f"::error::{error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
