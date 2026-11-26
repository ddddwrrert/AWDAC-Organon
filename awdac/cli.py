import argparse
import copy
from .settings import load
from pathlib import Path

from .enhancer import Enhancer
from .memory import Memory
from .schemas import canonical
from .integration.organon_adapter import snapshot, worker_context
from .reference import run


def main(argv=None):
    parser = argparse.ArgumentParser(prog="awdac")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("demo", "ablate"):
        demo = sub.add_parser(command)
        demo.add_argument("--db", default=":memory:")
        demo.add_argument("--config", type=Path, default=Path(__file__).with_name("default.toml"))
    audit = sub.add_parser("inspect-original")
    audit.add_argument("task", type=Path)
    audit.add_argument("--parent")
    args = parser.parse_args(argv)
    if args.command == "inspect-original":
        result = worker_context(args.task, args.parent) if args.parent else snapshot(args.task)
    else:
        config = load(args.config)
        if args.command == "demo":
            with Memory(args.db) as memory:
                result = run(Enhancer(memory, config), config)
        else:
            result = {}
            profiles = config.get("ablation", {"full": list(config["features"]), "baseline": [],
                                               **{key: [key] for key in config["features"]}})
            for name, enabled in profiles.items():
                variant = copy.deepcopy(config)
                variant["features"] = {key: value and key in enabled
                                       for key, value in config["features"].items()}
                with Memory(":memory:") as memory:
                    result[name] = run(Enhancer(memory, variant), variant)
    print(canonical(result))
