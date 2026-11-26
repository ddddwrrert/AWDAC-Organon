import argparse
from pathlib import Path
import sys

from awdac.cli import main
from awdac.enhancer import Enhancer
from awdac.integration.evaluation_adapter import prepare_ahc015
from awdac.integration.event_hooks import sync_run
from awdac.memory import Memory
from awdac.schemas import canonical
from awdac.settings import load

if __name__ == "__main__":
    if sys.argv[1:2] == ["prepare-ahc015"]:
        parser = argparse.ArgumentParser()
        parser.add_argument("destination")
        parser.add_argument("--original", default=Path(__file__).resolve().parents[1] / "Organon_original")
        args = parser.parse_args(sys.argv[2:])
        print(prepare_ahc015(args.original, args.destination))
    elif sys.argv[1:2] == ["sync-ahc015"]:
        parser = argparse.ArgumentParser()
        parser.add_argument("task")
        parser.add_argument("--db", required=True)
        args = parser.parse_args(sys.argv[2:])
        with Memory(args.db) as memory:
            print(canonical(sync_run(args.task, Enhancer(memory, load()))))
    else:
        main(["demo", *sys.argv[1:]])
