import ast
from dataclasses import dataclass


@dataclass(frozen=True)
class Capability:
    symbol: str
    role: str
    dependencies: tuple[str, ...]
    fingerprint: str
    status: str
    evidence: str


def profile(source, traces=(), controlled_findings=None):
    """Profile static function structure and attach supplied evidence by symbol."""
    from ..schemas import digest

    tree = ast.parse(source)
    nodes = {node.name: node for node in tree.body
             if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    controlled_findings = controlled_findings or {}
    result = []
    for name, node in nodes.items():
        dependencies = sorted({item.func.id for item in ast.walk(node)
                               if isinstance(item, ast.Call) and isinstance(item.func, ast.Name)
                               and item.func.id in nodes})
        role = next((role for prefix, role in (
            ("init", "initialization"), ("neighbor", "neighborhood"),
            ("accept", "acceptance"), ("score", "objective"),
            ("state", "state representation"), ("solve", "solver")
        ) if name.lower().startswith(prefix)), "unknown")
        fingerprint = digest(ast.dump(node, include_attributes=False))
        if fingerprint in controlled_findings:
            status, evidence = "validated", controlled_findings[fingerprint]
        elif name in traces:
            status, evidence = "observed", "Present in supplied execution trace"
        elif role != "unknown":
            status, evidence = "hypothesized", "Role inferred from symbol name"
        else:
            status, evidence = "unknown", "Static function declaration"
        result.append(Capability(name, role, tuple(dependencies), fingerprint, status, evidence))
    return result


def changes(parent, child):
    before = {item.symbol: item.fingerprint for item in parent}
    after = {item.symbol: item.fingerprint for item in child}
    return {"removed": sorted(before.keys() - after.keys()),
            "added": sorted(after.keys() - before.keys()),
            "changed": sorted(name for name in before.keys() & after.keys()
                              if before[name] != after[name])}
