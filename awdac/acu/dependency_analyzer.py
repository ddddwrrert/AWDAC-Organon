from .algorithm_profiler import profile

def dependencies(source):
    return {row.symbol: row.dependencies for row in profile(source)}
