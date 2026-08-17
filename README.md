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
  5. Sign in to the App Store (`mas` can no longer sign in for you, and the
     `mas` tasks are skipped for anything not already purchased).
  6. Install the required roles and collections:

     ```sh
     ansible-galaxy install -r requirements.yml
     ansible-galaxy collection install -r requirements.yml
     ```

  7. Run the playbook, entering your macOS account password at the `BECOME` prompt:

     ```sh
     ansible-playbook main.yml --ask-become-pass
     ```

> Note: If some Homebrew commands fail, you may need to agree to Xcode's license
> or fix another Brew issue. Run `brew doctor` to check.

### Running a specific set of tagged tasks

Filter which part of the provisioning process runs with `ansible-playbook`'s
`--tags` flag. Available tags: `homebrew`, `dotfiles`, `mas`, `dock`, `sudoers`,
`terminal`, `osx`, `extra-packages`, `vscode`, and `post`.

    ansible-playbook main.yml -K --tags "homebrew,mas"

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

My [dotfiles](https://github.com/seadogger/dotfiles) can also be installed into
the current user's home directory, including the `.osx` dotfile for configuring
many aspects of macOS. Dotfiles management is off by default here
(`configure_dotfiles: false`) because `~/dotfiles` is already cloned; set it to
`true` on a fresh machine.

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
