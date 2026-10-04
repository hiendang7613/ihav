# ihav

One catalog for the **ihav** family of plugins for Claude Code and Codex.

Every ihav plugin, public or private, and how they depend on each other. Only public plugins with a pinned
release are in this catalog; private ones are listed so the family stays visible in one place.

<!-- plugins:begin -->

| Plugin | Repository | In this catalog | What it does |
|---|---|---|---|
| [ihav-agent-room](https://github.com/hiendang7613/ihav-agent-room) | public | v0.7.0 | Native Claude Code and Codex agent rooms with shared tasks, peer messaging, a machine agents space and cross-room contracts. |
| [ihav-asd-ste100](https://github.com/hiendang7613/ihav-asd-ste100) | public | v0.19.1 | Short, plain, predictable replies in any language: key-first bullets, a one-sentence Conclusion, then eight fixed status sections. |
| [ihav-leaderboards](https://github.com/hiendang7613/ihav-leaderboards) | public | v0.2.2 | Merge the most-visited public leaderboards for any domain into one quality-first leaderboard with Pareto charts. |
| [ihav-web-visit-counter](https://github.com/hiendang7613/ihav-web-visit-counter) | public | v0.1.1 | Estimated monthly visits of a website, with date and source, no API key. |
| [ihav-competitor-search](https://github.com/hiendang7613/ihav-competitor-search) | private | no | Offline competitor synthesis; the live survey is not implemented yet. |
| [ihav-web-chat](https://github.com/hiendang7613/ihav-web-chat) | private | no | Browser-driven fan-out of one prompt to many web chatbots (unofficial, alpha). |
| [ihav-web-imagen](https://github.com/hiendang7613/ihav-web-imagen) | private | no | Draw with the ChatGPT account you already have, from Claude Code and Codex; formerly gpt-web-imagen. |

```mermaid
flowchart LR
  ihav_agent_room["ihav-agent-room"]
  ihav_asd_ste100["ihav-asd-ste100"]
  ihav_leaderboards["ihav-leaderboards"]
  ihav_web_visit_counter["ihav-web-visit-counter"]
  ihav_competitor_search("ihav-competitor-search (private)")
  ihav_web_chat("ihav-web-chat (private)")
  ihav_web_imagen("ihav-web-imagen (private)")
  ihav_agent_room -->|declared| ihav_asd_ste100
  ihav_leaderboards -->|declared| ihav_web_visit_counter
  ihav_leaderboards -.->|sends the discovery prompt to web chatbots (not released yet)| ihav_web_chat
  ihav_competitor_search -.->|runs its visits script for traffic numbers| ihav_web_visit_counter
  ihav_web_chat -.->|reuses its ChatGPT send-button finding| ihav_web_imagen
```

Solid arrows are dependencies declared in a plugin's manifest; the host installs them together. Dashed arrows are runtime or contract links that are not declared. Rounded boxes are private repositories.

<!-- plugins:end -->

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

Each entry is pinned to a release tag and its commit, so an install always gets a tested release.

Each plugin keeps its own repository, issues and releases. This repository holds only the two catalog files: `.claude-plugin/marketplace.json` for Claude Code and `.agents/plugins/marketplace.json` for Codex.

## Adding or updating a plugin

Open a pull request that changes both catalog files the same way: `.claude-plugin/marketplace.json` and
`.agents/plugins/marketplace.json`. Pin a release tag and its commit sha. The `check catalog` workflow runs
`scripts/check_catalog.py`: it confirms each tag resolves to its sha, the manifest at that commit carries the entry's
name, every declared dependency is in this catalog and matches `plugins.json`, and the plugin map in this README is
current. Add or change a plugin in `plugins.json` (any visibility), then run `python3 scripts/render_readme.py`. Merge when it passes.

Work in your own clone or `git worktree`, not in a folder another room or session also uses: a checkout or
branch switch there can overwrite someone else's uncommitted change. Direct pushes to `main` are blocked for
everyone, including admins.

## License

MIT. Each plugin has its own license in its repository.
