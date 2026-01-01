#!/usr/bin/env python3
"""Build a workspace manifest for repository files."""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone


DEFAULT_IGNORES = {
    ".git",
    "__pycache__",
    ".venv",
    "node_modules",
    ".pytest_cache",
    ".tox",
    "dist",
    "build",
}


def build_manifest(root: str, ref: str, output_path: str, ignores=None) -> None:
    """Create a manifest of files with sizes and SHA-256 hashes."""
    ignores = set(ignores or [])
    files = []
    total_size = 0

    for current_root, dirs, filenames in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ignores]
        for name in filenames:
            path = os.path.join(current_root, name)
            rel = os.path.relpath(path, root)
            try:
                with open(path, "rb") as fh:
                    data = fh.read()
            except OSError as exc:
                print(f"Skipping {rel}: {exc}", file=sys.stderr)
                continue

            sha = hashlib.sha256(data).hexdigest()
            size = len(data)
            total_size += size
            files.append(
                {"path": rel.replace("\\", "/"), "size": size, "sha256": sha}
            )

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ref": ref,
        "summary": {"file_count": len(files), "total_size_bytes": total_size},
        "files": sorted(files, key=lambda f: f["path"]),
    }

    with open(output_path, "w") as f:
        json.dump(manifest, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate workspace manifest.")
    parser.add_argument("--ref", default="", help="Ref used for manifest metadata")
    parser.add_argument(
        "--root", default=".", help="Repository root to scan (default: .)"
    )
    parser.add_argument(
        "--output",
        default="/tmp/workspace_manifest.json",
        help="Output path for manifest file",
    )
    args = parser.parse_args()

    build_manifest(args.root, args.ref, args.output, DEFAULT_IGNORES)


if __name__ == "__main__":
    main()
