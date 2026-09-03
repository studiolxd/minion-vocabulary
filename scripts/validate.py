#!/usr/bin/env python3
"""Validates every pack and regenerates manifest.toml.

A tiny script rather than a real build tool: this repository has no other
reason to need a toolchain, and Minion's own CI already runs on plain
Python + curl. Parsing uses tomllib (3.11+) so nothing needs installing.
"""

import hashlib
import pathlib
import sys

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # local dev on an older Python

ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKS_DIR = ROOT / "packs"
MANIFEST_PATH = ROOT / "manifest.toml"

# Bumped by hand when a release is cut — see the README.
VERSION = "2026.09.03"


def sha256_of(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_packs() -> list[pathlib.Path]:
    return sorted(PACKS_DIR.rglob("*.toml"))


def validate(packs: list[pathlib.Path]) -> None:
    errors = []
    for pack in packs:
        try:
            with pack.open("rb") as f:
                tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            errors.append(f"{pack.relative_to(ROOT)}: {e}")
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        sys.exit(1)


def write_manifest(packs: list[pathlib.Path]) -> None:
    lines = [f'version = "{VERSION}"']
    for pack in packs:
        rel = pack.relative_to(ROOT).as_posix()
        digest = sha256_of(pack)
        lines.append("")
        lines.append("[[packs]]")
        lines.append(f'path = "{rel}"')
        lines.append(f'sha256 = "{digest}"')
    MANIFEST_PATH.write_text("\n".join(lines) + "\n")


def main() -> None:
    packs = find_packs()
    if not packs:
        print("error: no .toml files found under packs/", file=sys.stderr)
        sys.exit(1)
    validate(packs)
    write_manifest(packs)
    print(f"validated {len(packs)} pack(s), wrote {MANIFEST_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
