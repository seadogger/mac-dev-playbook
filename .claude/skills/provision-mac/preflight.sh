#!/usr/bin/env bash
# Preflight readiness checks for the mac-dev-playbook.
#
# Verifies this Mac has everything needed to run `ansible-playbook main.yml`
# WITHOUT sudo (become defaults off; see main.yml). Prints a per-check report
# and a final VERDICT line.
#
# Exit codes:
#   0  READY            - prerequisites satisfied; safe to run the playbook
#   2  NEEDS_BOOTSTRAP  - bare Mac (no Homebrew); needs the one-time sudo bootstrap
#   1  NOT_READY        - a fixable prerequisite is missing; fix, then re-run
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$REPO" || { echo "cannot cd to repo root ($REPO)"; exit 1; }

if [ -t 1 ]; then
  green="$(tput setaf 2 2>/dev/null || true)"; red="$(tput setaf 1 2>/dev/null || true)"
  yellow="$(tput setaf 3 2>/dev/null || true)"; bold="$(tput bold 2>/dev/null || true)"
  reset="$(tput sgr0 2>/dev/null || true)"
else
  green=""; red=""; yellow=""; bold=""; reset=""
fi

PASS=0; WARN=0; FAIL=0; BOOTSTRAP=0
ok()   { printf "  ${green}✓${reset} %s\n" "$1"; PASS=$((PASS+1)); }
warn() { printf "  ${yellow}!${reset} %s\n" "$1"; WARN=$((WARN+1)); }
bad()  { printf "  ${red}✗${reset} %s\n" "$1"; FAIL=$((FAIL+1)); }

printf "%sPreflight checks for mac-dev-playbook%s\n" "$bold" "$reset"
printf "  repo: %s\n  user: %s\n\n" "$REPO" "$(whoami)"

# 1. Platform ---------------------------------------------------------------
arch="$(uname -m)"
if [ "$arch" = "arm64" ]; then
  ok "Apple Silicon (arm64)"
else
  warn "Architecture is $arch, not arm64 — homebrew_install_path is pinned to /opt/homebrew/Homebrew for Apple Silicon; override it in config.yml on Intel"
fi

# 2. Xcode / Command Line Tools --------------------------------------------
if xcode-select -p >/dev/null 2>&1; then
  ok "Xcode / Command Line Tools active ($(xcode-select -p))"
else
  bad "No active developer dir — install Xcode from the App Store, or run: xcode-select --install"
fi

# 3. Homebrew ---------------------------------------------------------------
if command -v brew >/dev/null 2>&1; then
  ok "Homebrew installed ($(brew --version 2>/dev/null | head -1))"
  prefix="$(brew --prefix 2>/dev/null)"
  repo="$(brew --repository 2>/dev/null)"
  [ "$prefix" = "/opt/homebrew" ] && ok "brew prefix is /opt/homebrew" \
    || warn "brew --prefix is '$prefix' (config assumes /opt/homebrew)"
  [ "$repo" = "/opt/homebrew/Homebrew" ] && ok "brew repository matches homebrew_install_path" \
    || warn "brew --repository is '$repo' (config pins /opt/homebrew/Homebrew)"
  # Routine runs have become OFF, so the prefix must already be user-owned.
  if [ -w /opt/homebrew ]; then
    ok "/opt/homebrew is writable by $(whoami)"
  else
    bad "/opt/homebrew not writable by $(whoami) — routine runs have become OFF. Fix: sudo chown -R $(whoami) /opt/homebrew"
  fi
else
  bad "Homebrew NOT installed — this is a bare Mac"
  BOOTSTRAP=1
fi

# 4. Ansible ----------------------------------------------------------------
if command -v ansible-playbook >/dev/null 2>&1; then
  ok "Ansible installed ($(ansible --version 2>/dev/null | head -1))"
else
  bad "ansible-playbook not found — install with: brew install ansible"
fi

# 5. Galaxy roles + collection ---------------------------------------------
if [ -d roles/elliotweiser.osx-command-line-tools ] && [ -d roles/geerlingguy.dotfiles ]; then
  ok "Galaxy roles installed (roles/)"
else
  bad "Galaxy roles missing — run: ansible-galaxy install -r requirements.yml"
fi
if command -v ansible-galaxy >/dev/null 2>&1 \
   && ansible-galaxy collection list 2>/dev/null | grep -qiE '^geerlingguy\.mac[[:space:]]'; then
  ok "geerlingguy.mac collection installed"
else
  bad "geerlingguy.mac collection missing — run: ansible-galaxy collection install -r requirements.yml"
fi

# 6. App Store sign-in for the mas role (soft) ------------------------------
if command -v mas >/dev/null 2>&1; then
  if acct="$(mas account 2>/dev/null)" && [ -n "$acct" ]; then
    ok "Signed in to the App Store as $acct"
  else
    warn "App Store sign-in not detected (mas can no longer sign in for you). Sign in via the App Store app, or the 'mas' tasks will fail. On recent macOS 'mas account' may report nothing even when signed in."
  fi
else
  warn "mas not on PATH yet — it's in the config and will be installed; sign in to the App Store before the 'mas' tag runs"
fi

# 7. Network (soft) ---------------------------------------------------------
if curl -fsS --max-time 5 https://formulae.brew.sh >/dev/null 2>&1; then
  ok "Network reachable (brew API)"
else
  warn "Could not reach the brew API in 5s (offline?) — package installs need network"
fi

# Verdict -------------------------------------------------------------------
printf "\n%sSummary:%s %d passed, %d warnings, %d failed\n" "$bold" "$reset" "$PASS" "$WARN" "$FAIL"
if [ "$BOOTSTRAP" = "1" ]; then
  printf "%sVERDICT: NEEDS_BOOTSTRAP%s\n" "$bold" "$reset"
  exit 2
elif [ "$FAIL" -gt 0 ]; then
  printf "%sVERDICT: NOT_READY%s\n" "$bold" "$reset"
  exit 1
else
  printf "%sVERDICT: READY%s\n" "$bold" "$reset"
  exit 0
fi
