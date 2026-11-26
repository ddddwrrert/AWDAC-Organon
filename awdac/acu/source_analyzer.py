import ast

def analyze(source):
    tree = ast.parse(source)
    return {"functions": [node.name for node in ast.walk(tree)
                          if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))],
            "imports": sorted({alias.name for node in ast.walk(tree)
                               if isinstance(node, (ast.Import, ast.ImportFrom))
                               for alias in node.names})}
