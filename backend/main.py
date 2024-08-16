import uvicorn
import os


if __name__ == "__main__":
    match os.environ["MODE"]:
        case "DEVELOPMENT":
            print("il Server si avvia in modalità DEVELOPMENT")
            uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

        case "PRODUCTION":
            print("il Server si avvia in modalità PRODUCTION")
            uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)

        case _:
            print(
                "ERROR: nessuna modalità di run (PROD/DEV) è stata definita nella variabili d'ambiente"
            )
