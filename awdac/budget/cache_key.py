from dataclasses import asdict
from ..schemas import digest

def cache_key(source, condition):
    return digest([digest(source), asdict(condition)])
