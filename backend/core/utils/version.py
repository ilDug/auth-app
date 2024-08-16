from pathlib import Path


def fastapi_version():
    """restituisce la versione installata di fastapi"""
    version = ""
    requirements = Path(__file__).parents[2] / "requirements.txt"

    with requirements.open() as file:
        for line in file:
            if "fastapi==" in line:
                version = line.rstrip().split("==")[1]
    return version
