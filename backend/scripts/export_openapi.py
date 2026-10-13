"""Export OpenAPI JSON schema from FastAPI application."""

import json
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from main import app


def export_openapi(output_path: Path = None):
    target = output_path or (backend_dir / "openapi.json")
    schema = app.openapi()
    with open(target, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
    print(f"OpenAPI schema successfully exported to: {target}")


if __name__ == "__main__":
    export_openapi()
