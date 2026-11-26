import argparse
from awdac.reporting.experiment_report import report

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task")
    args = parser.parse_args()
    print(report(args.task))
