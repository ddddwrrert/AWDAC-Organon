import argparse
import json
from pathlib import Path

def compare(left, right):
    if left["backend"] != right["backend"] or left["budget"]["max"] != right["budget"]["max"]:
        raise ValueError("Different backends or budgets")
    return {"fitness_delta": right["best_fitness"] - left["best_fitness"],
            "left_cost": left["cost"], "right_cost": right["cost"]}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("results", nargs=2, type=Path)
    args = parser.parse_args()
    print(json.dumps(compare(*(json.loads(path.read_text(encoding="utf-8-sig"))
                               for path in args.results))))
