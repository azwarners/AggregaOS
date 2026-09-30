import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path):
    return json.loads((ROOT / relative_path).read_text())


class Phase1ExampleSchemaTests(unittest.TestCase):
    def test_examples_match_schemas(self):
        examples = load_json("examples/v1/composition.json")
        redless = next(flow for flow in examples["flows"] if flow["id"] == "bounded-redless-task")
        semaphore = next(flow for flow in examples["flows"] if flow["id"] == "ladcemas-semaphore-change")
        cases = [
            ("host.schema.json", examples["host"]),
            ("application.schema.json", examples["application"]),
            ("adapter-result.schema.json", semaphore["adapter"]),
            ("execution-request.schema.json", redless["task"]),
            ("execution-result.schema.json", redless["result"]),
        ]

        for schema_name, instance in cases:
            with self.subTest(schema=schema_name):
                schema = load_json(f"schemas/v1/{schema_name}")
                Draft202012Validator.check_schema(schema)
                Draft202012Validator(schema).validate(instance)


if __name__ == "__main__":
    unittest.main()
