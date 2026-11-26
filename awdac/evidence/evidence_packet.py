from ..schemas import digest

def packet(record):
    return {"id": digest(record), "record": record}
