"""Deterministic toy optimizer. Only internally generated Python is executed."""
import random
import statistics
from dataclasses import asdict
from uuid import uuid4

from .operators.operator_discovery import implement_reference_operator
from .budget.result_reuse import evaluate_reference
from .budget.cost_report import summarize
from .schemas import Candidate, Condition, Intent, Proposal, Seed

BASELINE = """def initialize(values):
    return values[0]

def solve(values):
    return initialize(values)
"""
OPERATOR = implement_reference_operator("neighborhood", "max(values)")


class ReferenceAgent:
    def propose(self, context):
        if not context["population"]:
            return None
        return Proposal("Initialization may be the limiting factor",
                        f"Incumbent: {context['population'][-1]['fitness']}")


class ReferenceWorker:
    def create(self, parent, context, recommendation):
        if parent.source == OPERATOR:
            return Candidate(parent.source)
        return Candidate(OPERATOR, Intent(
            "radical", "The solver can select the best feasible element",
            "Parent picks the first element", "Replace the initializer with a max operator",
            "Higher objective", "Linear scan cost", "Compare the existing paired seed results",
            "Search coverage explains the gap better than initialization" if recommendation else "",
            ("replace:initialize", "create:neighborhood")))


def evaluate(source, condition):
    namespace = {"__builtins__": {"max": max}}
    try:
        code = compile(source, "<reference candidate>", "exec")
    except SyntaxError:
        return {"status": "compile_error", "fitness": 0, "seeds": []}
    try:
        exec(code, namespace)
    except Exception:
        return {"status": "runtime_error", "fitness": 0, "seeds": []}
    rows = []
    for seed in condition.seeds:
        rng = random.Random(seed)
        values = tuple(rng.sample(range(1, 100), 8))
        try:
            value = namespace["solve"](values)
        except Exception:
            return {"status": "runtime_error", "fitness": 0,
                    "seeds": [asdict(row) for row in rows]}
        feasible = type(value) is int and value in values
        rows.append(Seed(seed, value if feasible else None, feasible=feasible,
                         status="success" if feasible else "invalid_output",
                         features={"size": len(values)}))
    success = all(row.feasible for row in rows)
    return {"status": "success" if success else "invalid_output",
            "fitness": statistics.mean(row.score for row in rows) if success else 0,
            "seeds": [asdict(row) for row in rows]}


def run(enhancer, config, agent=None, worker=None):
    agent, worker = agent or ReferenceAgent(), worker or ReferenceWorker()
    settings = config["reference"]
    limit = settings["budget"]
    if type(limit) is not int or limit < 0:
        raise ValueError("Reference budget must be a nonnegative integer")
    condition = Condition("reference-max", "reference-evaluator-v1", "python-reference-v1",
                          "8 distinct integers from 1..99", "arithmetic-mean-v1",
                          tuple(settings["seeds"]), "max")
    run_id = str(uuid4())
    population = []
    counts = {"evaluation_calls": 0, "cache_hits": 0, "evaluated_seeds": 0}

    def official(candidate):
        return evaluate_reference(enhancer.memory, candidate, condition, evaluate,
                                  counts, reuse=enhancer.features["reuse"])

    parent = Candidate(BASELINE)
    parent_id = "c000000"
    previous = official(parent)
    enhancer.feedback(run_id, parent_id, parent, condition, previous)
    population.append({"id": parent_id, "fitness": previous["fitness"]})
    for index in range(1, limit + 1):
        context = enhancer.context(parent.source, BASELINE, condition, population)
        advice = agent.propose(context) if enhancer.features["collaboration"] else None
        child = worker.create(parent, context, advice)
        child_id = f"c{index:06}"
        result = official(child)
        enhancer.feedback(run_id, child_id, child, condition, result,
                          parent_id, parent, previous, advice)
        population.append({"id": child_id, "fitness": result["fitness"]})
        if result["status"] == "success" and result["fitness"] > previous["fitness"]:
            parent, parent_id, previous = child, child_id, result
    return {"backend": "reference", "run_id": run_id,
            "budget": {"max": limit, "used": limit, "remaining": 0},
            "best_candidate": parent_id, "best_fitness": previous["fitness"],
            "population": population, "cost": summarize(counts), "tokens": None}
