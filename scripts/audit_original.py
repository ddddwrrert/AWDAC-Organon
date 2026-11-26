import json
from pathlib import Path
import sys

def audit(root):
    entries = {
        "session": "plugins/dsh-evolve-loop/presets/evolve.patch.yml",
        "mutation": "plugins/dsh-evolve-loop/src/providers/mutate.js",
        "evaluation": "plugins/dsh-evolve-loop/src/providers/evaluate.js",
        "loop": "plugins/dsh-evolve-loop/src/providers/loop.js",
    }
    return {key: {"path": name, "present": (root / name).is_file()}
            for key, name in entries.items()}

if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Organon_original")
    result = audit(root)
    print(json.dumps(result, indent=2))
    raise SystemExit(int(not all(item["present"] for item in result.values())))
