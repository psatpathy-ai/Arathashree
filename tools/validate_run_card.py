import json
import sys
from pathlib import Path
from jsonschema import validate, ValidationError

SCHEMA_PATH = Path(__file__).parent.parent / 'src' / 'arthashree' / 'schemas' / 'run_card_schema.json'


def main(path):
    schema = json.loads(SCHEMA_PATH.read_text())
    data = json.loads(Path(path).read_text())
    try:
        validate(instance=data, schema=schema)
        print(f"Run-card at {path} is valid")
        return 0
    except ValidationError as e:
        print(f"Run-card validation failed: {e}")
        return 2


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: validate_run_card.py <path-to-run-card.json>")
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
