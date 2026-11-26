from dataclasses import asdict

def operators(capabilities):
    return [asdict(row) for row in capabilities if row.role == "neighborhood"]
