from pathlib import Path
import hashlib
import json
import sys


def verify(root, manifest):
    expected = json.loads(manifest.read_text(encoding="utf-8"))
    actual = {file.relative_to(root).as_posix(): hashlib.sha256(file.read_bytes()).hexdigest()
              for file in root.rglob("*") if file.is_file()
              and ".git" not in file.relative_to(root).parts}
    differences = sorted(name for name in actual.keys() | expected.keys()
                         if actual.get(name) != expected.get(name))
    if differences:
        raise SystemExit("\n".join(differences))
    print(f"Verified {len(expected)} original files")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "Organon_original"
    verify(source, root / "docs/original-sha256.json")
