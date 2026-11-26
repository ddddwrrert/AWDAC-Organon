from dataclasses import asdict

from .acu import changes, profile
from .evidence import attribution, diagnose, paired
from .discovery.bottleneck_discovery import discover
from .discovery.evidence_calibration import reliability
from .discovery.hypothesis_registry import registry
from .operators.operator_profiler import operators
from .operators.operator_contribution import operator_feedback
from .evidence.seed_collector import collect
from .schemas import digest


def available_profile(source):
    try:
        return profile(source)
    except SyntaxError:
        return []


class Enhancer:
    """Context and feedback only. The caller owns candidate and survival decisions."""

    def __init__(self, memory, config):
        self.memory = memory
        self.features = config["features"]
        self.collapse = config["evidence"]["collapse_fraction"]

    def context(self, parent, baseline, condition, population, observations=()):
        context = asdict(condition)
        history = self.memory.history(condition.task, context) if self.features["memory"] else []
        capabilities = available_profile(parent) if self.features["acu"] or self.features["operator"] else []
        report = {"population": population, "parent": [asdict(row) for row in capabilities],
                  "baseline": [asdict(row) for row in available_profile(baseline)] if self.features["acu"] else [],
                  "history": history, "condition": context}
        if self.features["m7"]:
            report["reliability"] = reliability(history)
        if (self.features["m9"] and (observations or history)) or (
                self.features["operator"] and observations):
            report["hypotheses"] = list(registry(discover(capabilities, history, observations)).values())
        if self.features["operator"]:
            report["operators"] = operators(capabilities)
        return report

    def feedback(self, run_id, candidate_id, candidate, condition, result,
                 parent_id=None, parent=None, previous=None, proposal=None):
        intent = candidate.intent
        evidence = None
        variation = None
        if previous is not None and self.features["seed"]:
            evidence = paired(collect(previous["seeds"]),
                              collect(result["seeds"]), condition, condition)
        if parent is not None and (self.features["acu"] or self.features["operator"]):
            try:
                variation = changes(profile(parent.source), profile(candidate.source))
            except SyntaxError:
                variation = None
        regression = None
        if self.features["regression"]:
            prior = previous["fitness"] if previous and previous["status"] == "success" else None
            regression = diagnose(result["status"], result["fitness"], prior, self.collapse, variation)
        record = {"evaluation": result, "paired": evidence, "regression": regression,
                  "proposal": asdict(proposal) if proposal else None,
                  "intent": asdict(intent) if intent and self.features["hdpe"] else None,
                  "comparison_id": digest([parent.source, candidate.source]) if parent else None}
        if parent is not None and self.features["eca"]:
            record["attribution"] = attribution(parent.source, candidate.source, intent, evidence)
        if self.features["operator"]:
            record["operator"] = operator_feedback(variation, intent, evidence)
        knowledge = {}
        if self.features["memory"]:
            if result["status"] == "success" and (previous is None or
                    (previous["status"] == "success" and result["fitness"] > previous["fitness"])):
                knowledge["program"] = {"source": candidate.source, "fitness": result["fitness"]}
            if intent:
                knowledge["algorithm"] = {"intent": asdict(intent), "source": candidate.source}
                if evidence and not evidence["unpaired"] and evidence["mean_delta"] < 0:
                    knowledge["counterexample"] = {"hypothesis": intent.hypothesis, "evidence": evidence}
        self.memory.save(run_id, candidate_id, condition.task, parent_id, asdict(condition),
                         candidate.source, record, knowledge)
        return record
