# ihav

One catalog for the **ihav** family of plugins for Claude Code and Codex.

| Plugin | What it does |
|---|---|
| [ihav-leaderboards](https://github.com/hiendang7613/ihav-leaderboards) | Merges the most-visited public leaderboards of any domain into one quality-first leaderboard, with a confidence for every score and a Pareto chart for every cost. |
| [ihav-asd-ste100](https://github.com/hiendang7613/ihav-asd-ste100) | Short, plain, predictable agent replies in any language. |
| [ihav-agent-room](https://github.com/hiendang7613/ihav-agent-room) | Native Claude Code + Codex agent rooms with shared tasks, peer messaging, reviews and native session recovery. Installs ihav-asd-ste100 with it. |
| [ihav-web-visit-counter](https://github.com/hiendang7613/ihav-web-visit-counter) | Monthly website traffic estimates with source and analysis date, or an honest rank when no estimate exists. |

More plugins join the catalog when their repositories are public.

## Install

Claude Code:

```bash
claude plugin marketplace add hiendang7613/ihav
claude plugin install ihav-leaderboards@ihav
```

Codex:

```bash
codex plugin marketplace add hiendang7613/ihav
codex plugin add ihav-leaderboards@ihav
```

Replace `ihav-leaderboards` with any plugin name in the table. Restart the host after installing.

Each entry is pinned to a release tag and its commit, so an install always gets a tested release. ihav-asd-ste100 has no release tag yet and still follows `main`.

Each plugin keeps its own repository, issues and releases. This repository holds only the two catalog files: `.claude-plugin/marketplace.json` for Claude Code and `.agents/plugins/marketplace.json` for Codex.

## Adding or updating a plugin

Open a pull request that changes both catalog files the same way: `.claude-plugin/marketplace.json` and
`.agents/plugins/marketplace.json`. Pin a release tag and its commit sha. The `check catalog` workflow runs
`scripts/check_catalog.py`: it confirms each tag resolves to its sha, the manifest at that commit carries the entry's
name, and every declared dependency is in this catalog. Merge when it passes.

## License

MIT. Each plugin has its own license in its repository.
