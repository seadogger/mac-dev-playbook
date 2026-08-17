#!/usr/bin/env python3
"""Compare default.config.yml against what is actually installed on this Mac.

Run after installing or removing software by hand to catch config drift:

    ./scripts/verify-config.py

Needs no setup: if the interpreter on PATH lacks PyYAML, the script re-execs
itself under Ansible's bundled Python, which has it.

Exits non-zero if drift is found, so it can be used in a pre-commit hook.
"""
import os
import shutil
import subprocess
import sys


def _reexec_with_pyyaml():
    """Re-run under an interpreter that has PyYAML.

    Homebrew's bare `python3` has no pyyaml, but Ansible bundles it -- and
    Ansible is a hard requirement of this repo anyway, so borrow its
    interpreter rather than making the user pip-install anything.
    """
    if os.environ.get("_VERIFY_CONFIG_REEXEC"):
        sys.exit(
            "error: no Python with PyYAML found.\n"
            "       Install Ansible (`brew install ansible`), or run:\n"
            "           uv run --with pyyaml scripts/verify-config.py"
        )

    candidates = []
    ansible = shutil.which("ansible")
    if ansible:  # the launcher's shebang points at the interpreter we want
        try:
            with open(ansible) as fh:
                first = fh.readline()
            if first.startswith("#!"):
                candidates.append(first[2:].strip().split()[0])
        except OSError:
            pass
    try:
        prefix = subprocess.run(["brew", "--prefix", "ansible"],
                                capture_output=True, text=True).stdout.strip()
        if prefix:
            candidates.append(os.path.join(prefix, "libexec/bin/python"))
    except OSError:
        pass
    candidates += ["/opt/homebrew/bin/python3", "/usr/bin/python3"]

    # NB: don't skip candidates that are the *same binary* as sys.executable.
    # Ansible's libexec/bin/python is a symlink to Homebrew's python3, so they
    # share an inode -- but it resolves a different venv site-packages, which is
    # exactly where PyYAML lives. The env guard above prevents an exec loop.
    env = {**os.environ, "_VERIFY_CONFIG_REEXEC": "1"}
    for py in candidates:
        if not (py and os.path.exists(py) and os.access(py, os.X_OK)):
            continue
        if subprocess.run([py, "-c", "import yaml"],
                          capture_output=True).returncode == 0:
            os.execve(py, [py, os.path.abspath(__file__), *sys.argv[1:]], env)

    sys.exit(
        "error: no Python with PyYAML found.\n"
        "       Install Ansible (`brew install ansible`), or run:\n"
        "           uv run --with pyyaml scripts/verify-config.py"
    )


try:
    import yaml
except ModuleNotFoundError:
    _reexec_with_pyyaml()

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(REPO, "default.config.yml")
CASKROOM = "/opt/homebrew/Caskroom"

# Formulae deliberately omitted from the config, with the reason.
FORMULA_EXCEPTIONS = {
    "ansible": "bootstrap dependency -- installing it from the playbook can upgrade Ansible mid-run",
}


def sh(cmd, required=False):
    """Run a command, returning its non-empty output lines.

    `required=True` means empty output indicates a broken environment rather
    than an empty machine -- e.g. `brew` returns nothing when HOME is unset,
    which would otherwise be misreported as "everything in the config is
    missing" instead of "the check could not run".
    """
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    lines = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
    if required and not lines:
        sys.exit(
            f"error: `{cmd}` produced no output (exit {r.returncode}).\n"
            f"       Refusing to report drift from a broken environment.\n"
            f"       stderr: {r.stderr.strip()[:300] or '(empty)'}"
        )
    return lines


def rename_shims():
    """Casks Homebrew keeps as symlinks after an upstream rename.

    `brew list --cask` prints both the old and new name, which would otherwise
    look like drift. Map old -> canonical target.
    """
    shims = {}
    if not os.path.isdir(CASKROOM):
        return shims
    for name in os.listdir(CASKROOM):
        path = os.path.join(CASKROOM, name)
        if os.path.islink(path):
            shims[name] = os.path.basename(os.readlink(path))
    return shims


def stale_casks(live):
    """Casks Homebrew still has a record for, but whose artifact is gone."""
    stale = []
    for c in live:
        arts = [a for a in sh(f'brew list --cask "{c}"') if a.endswith((".app", ".pkg"))]
        if not arts:
            continue
        primary = arts[0]
        base = os.path.basename(primary)
        if base.endswith(".app") and not os.path.exists(f"/Applications/{base}"):
            if not os.path.exists(primary):
                size = subprocess.run(
                    f'du -sh "{CASKROOM}/{c}" 2>/dev/null | cut -f1',
                    shell=True, capture_output=True, text=True).stdout.strip()
                stale.append((c, base, size))
    return stale


def report(title, cfg, live, exceptions=None):
    exceptions = exceptions or {}
    cfg, live = set(cfg), set(live)
    missing = sorted(cfg - live)
    extra = sorted(x for x in live - cfg if x not in exceptions)
    excused = sorted(x for x in live - cfg if x in exceptions)

    ok = not missing and not extra
    print(f"\n{'=' * 70}")
    print(f"{title}  [{'OK' if ok else 'DRIFT'}]")
    print(f"{'=' * 70}")
    print(f"  {len(cfg)} in config / {len(live)} installed")
    for x in missing:
        print(f"  - IN CONFIG, NOT INSTALLED: {x}")
    for x in extra:
        print(f"  + INSTALLED, NOT IN CONFIG: {x}")
    for x in excused:
        print(f"  ~ excluded on purpose:      {x}  ({exceptions[x]})")
    if ok:
        print("  exact match")
    return not ok


def main():
    with open(CFG) as f:
        c = yaml.safe_load(f)

    drift = False

    drift |= report("HOMEBREW FORMULAE  (brew leaves)",
                    c["homebrew_installed_packages"], sh("brew leaves", required=True),
                    FORMULA_EXCEPTIONS)

    shims = rename_shims()
    live_casks_raw = sh("brew list --cask", required=True)
    live_casks = {shims.get(x, x) for x in live_casks_raw}
    drift |= report("HOMEBREW CASKS  (brew list --cask)",
                    c["homebrew_cask_apps"], live_casks)
    if shims:
        print("  rename shims collapsed to canonical names:")
        for old, new in sorted(shims.items()):
            print(f"      {old} -> {new}")

    cfg_mas = {str(a["id"]) for a in c["mas_installed_apps"]}
    live_mas = {ln.split(None, 1)[0] for ln in sh("mas list", required=True)}
    drift |= report("MAC APP STORE  (mas list, by id)", cfg_mas, live_mas)

    code = "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
    if os.path.exists(code):
        drift |= report("VS CODE EXTENSIONS  (code --list-extensions)",
                        [e.lower() for e in c["visual_studio_code_extensions"]],
                        [e.lower() for e in sh(f'"{code}" --list-extensions')])

    stale = stale_casks(live_casks_raw)
    print(f"\n{'=' * 70}")
    print(f"STALE HOMEBREW RECORDS  [{'OK' if not stale else 'FOUND'}]")
    print(f"{'=' * 70}")
    if stale:
        print("  Homebrew still lists these, but the app is gone from /Applications.")
        print("  They will NOT be reinstalled by the playbook. To clear a record:")
        print("      brew uninstall --cask --force <name>\n")
        for name, app, size in stale:
            print(f"  ! {name:<22} {app:<28} {size:>6} in Caskroom")
    else:
        print("  none")

    print(f"\n{'=' * 70}")
    print("RESULT:", "DRIFT FOUND" if drift else "CONFIG MATCHES MACHINE")
    print("=" * 70)
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
