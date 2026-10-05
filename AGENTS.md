# Agent guide — mac-dev-playbook

Ansible playbook that provisions and configures this Mac (a customized fork of
[geerlingguy/mac-dev-playbook](https://github.com/geerlingguy/mac-dev-playbook)).
It is a declarative record of what belongs on the machine, not application code.

## The one rule: config is a mirror of the machine

`default.config.yml` is the **single source of truth** and is kept in exact sync
with what is actually installed. Each package list mirrors a real command:

| Config key | Mirrors | Notes |
|---|---|---|
| `homebrew_installed_packages` | `brew leaves` | Top-level formulae only. Do **not** list dependencies — Homebrew resolves them. |
| `homebrew_cask_apps` | `brew list --cask` | GUI apps *and* CLI casks (e.g. `codex`). |
| `mas_installed_apps` | `mas list` | Mac App Store apps, keyed by numeric id. |
| `visual_studio_code_extensions` | `code --list-extensions` | |

After changing any of these — or after installing/removing software by hand —
run the drift check and make it pass:

```sh
./scripts/verify-config.py
```

It diffs all four lists in both directions and exits non-zero on drift, so it
doubles as a pre-commit gate. It already understands Homebrew's rename symlinks
and lingering-but-dead cask records; don't work around it, fix the config.

## Conventions

- Keep each list **alphabetically sorted** (the existing lists are).
- When you remove something, don't delete the line — comment it out with a
  short reason and an absolute date (see the `# Removed 2026-08` entries).
  Convert any relative date to an absolute one.
- Machine-specific shell config goes in `templates/aliases.j2` (rendered to
  `~/.aliases`, which the upstream `.zshrc` sources) — **never** edit `~/.aliases`
  directly; the next run overwrites it. The dotfiles role only symlinks upstream
  files verbatim, so don't try to patch dotfiles here.

## Running it

```sh
ansible-playbook main.yml                         # full run; NO sudo — become defaults off (main.yml)
ansible-playbook main.yml --tags homebrew         # just Homebrew formulae + casks
```

Sudo is only for bare-Mac bootstrap (creating /opt/homebrew; CLT is moot since Xcode
comes from the mas list) — see README step 7 — and for installing a Mac App Store
app that isn't there yet: mas 7 installs as root, so `tasks/mas.yml` escalates that
one task (task-level `ansible_become: true`) only when an app is missing. Such a run
needs `ansible-playbook main.yml --tags mas --ask-become-pass`. Never use
`-e bootstrap=true` for this — it makes every task root and Homebrew refuses root.
Otherwise never add `--ask-become-pass` to routine runs; if a run demands become,
a new genuinely-root task crept in and needs review.

Available tags: `homebrew`, `dotfiles`, `mas`, `dock`, `sudoers`, `shell-local`,
`terminal`, `osx`, `extra-packages`, `vscode`, `post`.

Runs are idempotent — re-running only installs what's missing. `mas` is skipped
unless you're signed in to the App Store first.

First-time setup on a fresh machine (roles/collections must be present):

```sh
ansible-galaxy install -r requirements.yml
ansible-galaxy collection install -r requirements.yml
```

## Layout

- `main.yml` — the playbook: roles (command-line-tools, homebrew, dotfiles, dock)
  then task imports (mas, sudoers, shell-local, terminal, osx, extra-packages, vscode).
  `tasks/mas.yml` replaces the `geerlingguy.mac.mas` role.
- `default.config.yml` — all variables and package lists (the source of truth).
- `config.yml` — optional, **git-ignored** per-machine override; does not exist
  by default. `main.yml` includes it via a fileglob if present.
- `tasks/` — imported task files, one per tag.
- `templates/` — Jinja2 templates (`aliases.j2`, `sudoers.j2`).
- `scripts/verify-config.py` — the drift checker described above.
- `roles/` — vendored Galaxy roles (installed from `requirements.yml`).

## Gotchas already encoded in comments — respect them

- **Never add `ansible`** to `homebrew_installed_packages`: installing it mid-run
  can upgrade Ansible under itself. It's an intentional exception in the verifier.
- `homebrew_install_path` is pinned to `/opt/homebrew/Homebrew` on purpose;
  the role's default would recursively `chown` the whole prefix.
- Dotfiles clone to `~/Documents/dotfiles`, **not** `~/dotfiles` (that path still
  holds an old personal fork; a different remote there makes the git module fail).
- ansible-core 2.21+ requires `when:` conditionals to resolve to a real boolean,
  so list-driven gates use `| length > 0`, not bare truthiness.

## Agent skills

### Issue tracker

Issues live in GitHub Issues on seadogger/mac-dev-playbook (via `gh`). See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `GLOSSARY.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
