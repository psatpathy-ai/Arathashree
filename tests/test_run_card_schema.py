import json
from pathlib import Path
from jsonschema import validate


def test_run_card_example_valid():
    repo_root = Path(__file__).resolve().parents[1]
    schema_path = repo_root / 'src' / 'arthashree' / 'schemas' / 'run_card_schema.json'
    example = repo_root / 'tests' / 'fixtures' / 'run_card_example.json'

    schema = json.loads(schema_path.read_text())
    data = json.loads(example.read_text())
    # Should not raise
    validate(instance=data, schema=schema)
