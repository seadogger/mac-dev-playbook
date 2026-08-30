---
name: provision-mac
description: >
  Check this Mac is ready to run the mac-dev-playbook, then install it. Use when the
  user wants to provision, rebuild, re-run, or "install" this machine's dev
  configuration, or asks whether the Mac is ready to run the playbook. Runs preflight
  prerequisite checks (Homebrew, Ansible, Galaxy roles/collection, /opt/homebrew
  ownership, App Store sign-in, network) then runs `ansible-playbook main.yml` and
  confirms the result with verify-config.py.
---

# Provision this Mac with the dev playbook

Two phases: **preflight** (is the Mac ready?), then **install** (run the playbook).
Always run preflight first and act on its verdict — never jump straight to the
playbook.

## 1. Preflight

From the repo root, run the readiness script:

```sh
.claude/skills/provision-mac/preflight.sh
```

It prints a per-check `✓ / ! / ✗` report and ends with a `VERDICT:` line and a
matching exit code:

| Verdict | Exit | What to do |
|---|---|---|
| `READY` | 0 | Prerequisites satisfied — go to **Install**. |
| `NEEDS_BOOTSTRAP` | 2 | Bare Mac (no Homebrew). Do **not** run the routine playbook — use **Bootstrap** below. |
| `NOT_READY` | 1 | A fixable prerequisite is missing. Show the `✗` lines, apply the one-line fix each prints, then re-run preflight. Do not install until it returns READY. |

Warnings (`!`) don't block install, but relay them — e.g. an unverified App
Store sign-in means the `mas` tasks may fail until the user signs in.

## 2. Install

Only when preflight reports **READY**.

Routine run (already-provisioned Mac — **no sudo**; `become` defaults off in
`main.yml`):

```sh
ansible-playbook main.yml
```

Scope a run with `--tags` when you only want part of it (tags: `homebrew`,
`dotfiles`, `mas`, `dock`, `sudoers`, `shell-local`, `terminal`, `osx`,
`extra-packages`, `vscode`, `post`). Runs are idempotent — re-running only
installs what's missing.

## 3. Confirm

After the playbook finishes, verify the machine matches the config:

```sh
./scripts/verify-config.py
```

Expect `CONFIG MATCHES MACHINE` (exit 0). If it reports drift, reconcile per
`AGENTS.md`: `homebrew_installed_packages` mirrors `brew leaves`,
`homebrew_cask_apps` mirrors `brew list --cask`, `mas_installed_apps` mirrors
`mas list`, `visual_studio_code_extensions` mirrors `code --list-extensions`.

## Bootstrap (bare Mac only — preflight said NEEDS_BOOTSTRAP)

This is the one path that needs sudo, and only once. These are interactive and
best run by the user directly:

1. Install **Xcode** from the App Store first (it provides the Command Line
   Tools), or run `xcode-select --install`.
2. Install **Homebrew**, then put it on `PATH`:
   ```sh
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
   eval "$(/opt/homebrew/bin/brew shellenv)"
   ```
3. Make sure the prefix is user-owned (routine runs assume this):
   ```sh
   sudo mkdir -p /opt/homebrew && sudo chown "$(whoami)" /opt/homebrew
   ```
4. Install Ansible and the Galaxy dependencies:
   ```sh
   brew install ansible
   ansible-galaxy install -r requirements.yml
   ansible-galaxy collection install -r requirements.yml
   ```
5. Sign in to the App Store (so the `mas` tasks work).
6. First provision, with the root-only tasks enabled:
   ```sh
   ansible-playbook main.yml -e bootstrap=true --ask-become-pass
   ```

After bootstrap, re-run preflight; from then on use the routine sudo-free command
in **Install**.
