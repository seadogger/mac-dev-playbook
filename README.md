# Mac Development Ansible Playbook

This playbook installs and configures my Mac for general use and software development.

*See also*:
  - [Mac Dev Playbook](https://github.com/geerlingguy/mac-dev-playbook) (upstream)
  - [osxc](https://github.com/osxc)
  - [MWGriffin/ansible-playbooks](https://github.com/MWGriffin/ansible-playbooks) (the original inspiration for this project)

## Installation

  1. Ensure Apple's command line tools are installed: `xcode-select --install`.
  2. Install Homebrew (this also bootstraps step 1 if you skipped it):

     ```sh
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     ```

     On Apple Silicon, Homebrew lives in `/opt/homebrew`, which is not on the
     default `$PATH`. Add it to your shell profile:

     ```sh
     echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
     eval "$(/opt/homebrew/bin/brew shellenv)"
     ```

  3. Install Ansible: `brew install ansible`
  4. Clone this repository to your local drive.
  5. Sign in to the App Store (`mas` can no longer sign in for you).
  6. Install the required roles and collections:

     ```sh
     ansible-galaxy install -r requirements.yml
     ansible-galaxy collection install -r requirements.yml
     ```

  7. Run the playbook.

     **Bare Mac (first bootstrap):** install Xcode from the App Store first (sign in,
     install — it's in the `mas` list anyway, and it provides the full toolchain, so
     the Command Line Tools role never needs to run). Then the only thing on the
     entire machine that genuinely requires root is creating Homebrew's prefix —
     one transparent command:

     ```sh
     sudo mkdir -p /opt/homebrew && sudo chown "$(whoami)" /opt/homebrew
     ansible-playbook main.yml
     ```

     (Headless fallback — no Xcode, CLT installed via `softwareupdate`, which is
     root-only: `ansible-playbook main.yml -e bootstrap=true --ask-become-pass`.)

     **Already-provisioned machine (routine re-runs):** no sudo — become
     defaults off and the formerly-privileged tasks verify state without root:

     ```sh
     ansible-playbook main.yml
     ```

     The one exception: installing a Mac App Store app that isn't there yet.
     `mas` 7 installs as root, so when `tasks/mas.yml` finds a missing app it
     escalates just that task. Give it your password for that run:

     ```sh
     ansible-playbook main.yml --tags mas --ask-become-pass
     ```

     (Don't use `-e bootstrap=true` for this — it makes every task root, and
     Homebrew refuses to run as root.)

> Note: If some Homebrew commands fail, you may need to agree to Xcode's license
> or fix another Brew issue. Run `brew doctor` to check.

### Running a specific set of tagged tasks

Filter which part of the provisioning process runs with `ansible-playbook`'s
`--tags` flag. Available tags: `homebrew`, `dotfiles`, `mas`, `dock`, `sudoers`, `shell-local`,
`terminal`, `osx`, `extra-packages`, `vscode`, and `post`.

    ansible-playbook main.yml --tags "homebrew,mas"

## Overriding Defaults

Not everyone's development environment and preferred software configuration is
the same. Override any of the defaults in `default.config.yml` by creating a
`config.yml` file (git-ignored) and setting the overrides there:

```yaml
homebrew_installed_packages:
  - cowsay
  - git
  - go

homebrew_cask_apps:
  - google-chrome

mas_installed_apps:
  - { id: 497799835, name: "Xcode" }

npm_packages:
  - name: webpack

configure_dock: true
dockitems_remove:
  - Launchpad
  - TV
dockitems_persist:
  - name: "Sublime Text"
    path: "/Applications/Sublime Text.app/"
    pos: 5
```

Any variable can be overridden in `config.yml`; see the supporting roles'
documentation for a complete list of available variables.

## What Gets Installed

`default.config.yml` is the single source of truth and is kept in sync with what
is actually installed on this Mac. It covers:

  - **Homebrew formulae** — `homebrew_installed_packages`, mirroring `brew leaves`
    (top-level installs only; dependencies are omitted since Homebrew resolves them).
  - **Homebrew casks** — `homebrew_cask_apps`, mirroring `brew list --cask`.
    Apps that were previously installed but aren't anymore are kept commented out
    so they're easy to restore.
  - **Mac App Store apps** — `mas_installed_apps`, mirroring `mas list`.
  - **VS Code extensions** — `visual_studio_code_extensions`, mirroring
    `code --list-extensions`.

### Checking for drift

After installing or removing software by hand, check the config still matches
the machine:

```sh
./scripts/verify-config.py
```

It diffs all four lists in both directions and exits non-zero on drift, so it
also works as a pre-commit hook. It understands two things a naive diff gets
wrong: Homebrew's rename symlinks (e.g. `handbrake` → `handbrake-app`) are
collapsed to their canonical names, and casks whose app has been deleted but
whose Homebrew record lingers are reported separately — those are invisible
otherwise, since the playbook sees them as already installed and skips them.

The underlying commands, if you'd rather check by hand:

```sh
brew leaves
brew list --cask
mas list
code --list-extensions
```

## Dotfiles

Dotfiles come straight from [geerlingguy/dotfiles](https://github.com/geerlingguy/dotfiles)
rather than a personal fork. The role clones that repo to `~/Documents/dotfiles`
and symlinks `.zshrc`, `.gitignore`, `.inputrc`, `.osx` and `.vimrc` into `$HOME`.

The role only symlinks — it has no merge step, so whatever upstream ships lands
verbatim. Machine-specific shell config therefore lives in `~/.aliases`, which
the upstream `.zshrc` already sources, rendered from
[`templates/aliases.j2`](templates/aliases.j2) by `tasks/shell-local.yml`. Edit
the template, not `~/.aliases` — the next run overwrites it.

The most important thing that file does is `typeset -U path PATH`. The upstream
`.zshrc` prepends nine entries to `PATH` unconditionally and runs for every
interactive shell, so without it each nested shell stacks another copy and `PATH`
grows without bound. Setting `-U` dedupes the array immediately and the attribute
persists, so later appends stay clean too.

`.osx` is taken as-is from upstream. Note that it is materially smaller than the
2021-era copy some forks still carry: Jeff has pruned settings that no longer
work on modern macOS, and a few that still do (Dock autohide timing, Finder
path bar, screenshot location, immediate screensaver password). If you want any
of those back, add them to a task in this repo rather than forking the dotfiles.

`.osx` runs on **every** playbook run via `osx_script`, under the `osx` tag.

## Manual Installs

These are installed by hand and are **not** managed by this playbook — the list
is what is actually on this Mac, verified against `/Applications`. Reinstall
them yourself after a rebuild.

| App | Size | Source |
|---|---|---|
| [PixInsight](https://pixinsight.com) | 3.1 GB | Paid download; requires a license |
| [Topaz Labs suite](https://www.topazlabs.com) (Video Enhance AI, DeNoise, Gigapixel, Sharpen, Mask, Studio 2) | 6.6 GB | Paid download; requires a license |
| [Original Prusa Drivers](https://www.prusa3d.com/drivers/) | 336 MB | Driver bundle — see note below |
| StellarMate | 113 MB | Sideloaded iPad app; not on the Mac App Store |
| stellarmatetools | — | Ships with StellarMate |
| [Epson Software](https://epson.com/support) (Connect Printer Setup, Scan 2) | 7.3 MB | Printer/scanner drivers |
| [CuaDriver](https://trycua.com) | — | Direct download |
| FloridaParkAvailability | 2.1 MB | Self-built app |

> Note: `Original Prusa Drivers` bundles its own copy of PrusaSlicer, which
> duplicates the `prusaslicer` Homebrew cask. Keep one or the other to avoid two
> versions drifting apart.

Astrophotography add-ons for PixInsight, all installed from within the app:
[StarNet++ v2 for Apple Silicon](https://www.starnetastro.com/download/),
[BatchFitsKeywordEdit](https://pixinsight.com/forum/index.php?threads/batch-edit-fits-headers.9389/page-3),
[GHS Script](https://ghsastro.co.uk/information/),
[HVB Scripts](http://www.skypixels.at/pixinsight_scripts.html#SKill),
[EZ Suite](https://pixinsight.com/forum/index.php?threads/ez-processing-suite.14937/),
[Star De-emphasizer](https://pixinsight.com/forum/index.php?threads/star-de-emphasizer-script-adam-blocks-star-reduction-method.16034/).

## Manual Configuration TODO

  1. Configure extra Mail and/or Calendar accounts (e.g. Google, Exchange, etc.).
  2. Enter the license code for MakeMKV.
  3. Set the FileBot default format string for video file conversion: `{plex}'-'{vf}{vc}.mkv`
  4. Install tunnels for WireGuard using the QR codes from the WireGuard server.
  5. Sign in to the App Store before running the `mas` tag.

## Troubleshooting

### The `code` command isn't found

The `vscode` tag looks for the CLI inside the app bundle, so it works without
`code` on your `$PATH`. To get `code` in your shell anyway, open VS Code, hit
⇧⌘P, and run **Shell Command: Install 'code' command in PATH**.

### `Unexpected Exception` or a removed-callback error on startup

An old `community.general` in `~/.ansible/collections` shadows the version
bundled with Homebrew's Ansible and can break the stdout callback. Check which
copy wins and remove the stale one:

    ansible-galaxy collection list community.general
    rm -rf ~/.ansible/collections/ansible_collections/community/general

### Homebrew reports a cask as installed, but the app is missing

Homebrew's Caskroom metadata can go stale if an app was deleted by hand. The
playbook will skip reinstalling it, so force it:

    brew reinstall --cask <name>

### Dock crashes and continuously restarts

    rm ~/Library/Application\ Support/Dock/desktoppicture.db

## Ansible for DevOps

Check out [Ansible for DevOps](https://www.ansiblefordevops.com/), which teaches
you how to automate almost anything with Ansible.

## Author

Seadogger, 2019. Forked from [Jeff Geerling](https://www.jeffgeerling.com/) - [Mac Dev Playbook](https://github.com/geerlingguy/mac-dev-playbook).
