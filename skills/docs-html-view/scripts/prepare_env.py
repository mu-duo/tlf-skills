#!/usr/bin/env python3
"""Prepare the docs render environment for docs-html-view.

Stdlib only. Never installs Python or uv, and never touches global/system
site-packages. It creates or reuses one *recognized* virtualenv and, only when
explicitly asked, installs the pinned requirements into that venv.

Run this only AFTER the user has approved the packages, the environment, and the
files (the Skill asks; this helper stores no consent state).
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

MIN_PY = (3, 12)


def venv_python(venv: str) -> str:
    if os.name == "nt":
        return os.path.join(venv, "Scripts", "python.exe")
    return os.path.join(venv, "bin", "python")


def is_recognized_venv(venv: str) -> bool:
    return os.path.isfile(os.path.join(venv, "pyvenv.cfg"))


def python_version(python: str):
    code = "import sys;print('%d.%d' % sys.version_info[:2])"
    try:
        out = subprocess.run(
            [python, "-I", "-c", code], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        return None, str(exc)
    try:
        return tuple(int(x) for x in out.split(".")[:2]), out
    except ValueError:
        return None, out


def run(cmd, cwd=None):
    print("+ " + " ".join(cmd))
    return subprocess.run(cmd, cwd=cwd)


def has_pip(python: str) -> bool:
    try:
        return subprocess.run(
            [python, "-m", "pip", "--version"], capture_output=True, text=True
        ).returncode == 0
    except OSError:
        return False


def venv_prefix(python: str):
    try:
        out = subprocess.run(
            [python, "-c", "import sys;print(sys.prefix)"], capture_output=True, text=True
        )
    except OSError:
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def pip_in_venv(python: str, venv: str):
    if not has_pip(python):
        return False, "pip is not available in the interpreter"
    prefix = venv_prefix(python)
    if prefix is None or os.path.realpath(prefix) != os.path.realpath(venv):
        return False, "interpreter does not belong to %s (sys.prefix=%s)" % (venv, prefix)
    return True, ""


def main() -> None:
    default_req = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), os.pardir, "requirements.txt"
    )
    ap = argparse.ArgumentParser(
        description="Create/reuse the docs render venv and optionally install pinned requirements."
    )
    ap.add_argument("--project-root", default=os.getcwd())
    ap.add_argument("--venv", default=".venv-docs", help="venv path (relative to project root unless absolute)")
    ap.add_argument("--base-python", default=None, help="interpreter used to create the venv (default: this one)")
    ap.add_argument("--requirements", default=default_req)
    ap.add_argument("--install", action="store_true", help="install the pinned requirements (post-consent)")
    ap.add_argument("--freeze", metavar="PATH", default=None, help="write `pip freeze` output to PATH (post-consent)")
    args = ap.parse_args()

    root = os.path.abspath(args.project_root)
    venv = args.venv if os.path.isabs(args.venv) else os.path.join(root, args.venv)
    requirements = os.path.abspath(args.requirements)

    if os.path.lexists(venv) and not is_recognized_venv(venv):
        sys.exit("refusing: %s exists but is not a virtualenv (no pyvenv.cfg); move it aside first" % venv)

    if not is_recognized_venv(venv):
        base = args.base_python or sys.executable
        ver, raw = python_version(base)
        if ver is None or ver < MIN_PY:
            sys.exit("refusing: %s reports %s; need Python >= %d.%d" % (base, raw, *MIN_PY))
        print("+ %s -m venv %s" % (base, venv))
        created = subprocess.run(
            [base, "-m", "venv", venv], capture_output=True, text=True
        )
        if created.returncode != 0:
            detail = (created.stderr or created.stdout or "").strip()
            sys.exit(
                "failed to create virtualenv at %s (exit %d).\n%s\n"
                "Ensure python3-venv/ensurepip is available, or pass --venv pointing at "
                "an existing project docs environment." % (venv, created.returncode, detail)
            )
    else:
        print("reusing virtualenv: " + venv)

    py = venv_python(venv)
    ver, raw = python_version(py)
    if ver is None or ver < MIN_PY:
        sys.exit("refusing: venv python reports %s; need Python >= %d.%d" % (raw, *MIN_PY))

    if args.install or args.freeze:
        ok, why = pip_in_venv(py, venv)
        if not ok:
            sys.exit("refusing: %s; point --venv at a working docs environment" % why)

    if args.install:
        if not os.path.isfile(requirements):
            sys.exit("requirements not found: " + requirements)
        result = run(
            [py, "-m", "pip", "install", "--no-input", "--disable-pip-version-check", "-r", requirements],
            cwd=root,
        )
        if result.returncode != 0:
            sys.exit("pip install failed (exit %d)" % result.returncode)

    if args.freeze:
        result = subprocess.run([py, "-m", "pip", "freeze"], capture_output=True, text=True)
        if result.returncode != 0:
            sys.exit("pip freeze failed (exit %d)" % result.returncode)
        dest = args.freeze if os.path.isabs(args.freeze) else os.path.join(root, args.freeze)
        os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
        with open(dest, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(result.stdout)
        print("wrote freeze: " + dest)

    print("python: " + py)
    print("install: " + ("yes" if args.install else "no"))


if __name__ == "__main__":
    main()
