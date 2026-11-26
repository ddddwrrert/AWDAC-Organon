from ..schemas import Seed

def collect(rows):
    seeds = [Seed(**row) for row in rows]
    if len({seed.id for seed in seeds}) != len(seeds):
        raise ValueError("Duplicate seed identifiers")
    return seeds
