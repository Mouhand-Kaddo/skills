# skills

Agent skills for Claude Code, Codex and other agents that support the `SKILL.md` format.

| Skill | What it does |
|---|---|
| [`phone-use`](skills/phone-use) | Run, test, reproduce a bug or verify a fix in an Android app on a real phone connected over ADB. Includes a preflight script that refuses emulators and ambiguous device targets. |
| [`stacked-prs`](skills/stacked-prs) | Create a stack of PRs, restack after a lower layer or trunk changes, repair a broken stack, or merge a stack in order. |

## Install

Any agent, via [skills](https://github.com/vercel-labs/skills):

```sh
npx skills add Mouhand-Kaddo/skills
```

Claude Code, as a plugin:

```
/plugin marketplace add Mouhand-Kaddo/skills
/plugin install mouhand-skills@mouhand-skills
```

Or copy a folder from `skills/` into `~/.claude/skills/` (or your agent's skills directory).

## Requirements

- `phone-use`: Android `adb`, Python 3, a physical Android device with USB debugging enabled.
- `stacked-prs`: `git` and a GitHub repo. Uses a stack tool such as `gh stack` if one is installed, but does not require one.

## License

MIT
