import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app

OUTPUT_PATH = ROOT / "docs" / "openapi.json"


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(app.openapi(), indent=2), encoding="utf-8")
    print(f"OpenAPI schema exported to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
