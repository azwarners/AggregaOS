import json
from pathlib import Path
import unittest

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path):
    return json.loads((ROOT / relative_path).read_text())


class CatalogContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_json("catalog/v1/index.json")
        cls.application_schema = load_json("schemas/v1/application.schema.json")
        cls.status_schema = load_json("schemas/v1/application-status.schema.json")

    def test_catalog_index_and_entries_match_schema(self):
        Draft202012Validator.check_schema(self.application_schema)
        validator = Draft202012Validator(self.application_schema)
        app_ids = set()

        for ref in self.catalog["applications"]:
            with self.subTest(application=ref["id"]):
                self.assertNotIn(ref["id"], app_ids)
                app_ids.add(ref["id"])
                entry = load_json(f"catalog/v1/{ref['path']}")
                self.assertEqual(entry["id"], ref["id"])
                validator.validate(entry)

                if entry["capabilities"]["install"]:
                    self.assertTrue(entry["install_methods"])
                    self.assertTrue(entry.get("entry_point"))
                    self.assertTrue((ROOT / entry["entry_point"]).is_file())
                    self.assertTrue(entry.get("platforms"))
                    self.assertTrue(entry.get("deployments"))
                else:
                    self.assertEqual(entry["status"], "blocked")
                    self.assertEqual(entry["install_methods"], [])

        self.assertEqual(len(app_ids), 17)

    def test_application_status_contract_accepts_catalog_verification_shape(self):
        Draft202012Validator.check_schema(self.status_schema)
        validator = Draft202012Validator(self.status_schema)
        for ref in self.catalog["applications"]:
            entry = load_json(f"catalog/v1/{ref['path']}")
            if not entry["capabilities"]["install"]:
                continue
            deployment = entry["deployments"][0]
            status = {
                "schema_version": "v1",
                "application_id": entry["id"],
                "state": "installed",
                "version": entry["version"],
                "deployment": {
                    "backend": deployment["backend"],
                    "method": deployment["method"],
                },
                "verification": {"status": "passed", "check": "catalog contract fixture"},
            }
            if entry.get("services"):
                status["deployment"]["service"] = entry["services"][0]["name"]
            if deployment.get("image"):
                status["deployment"]["image"] = deployment["image"]
            with self.subTest(application=entry["id"]):
                validator.validate(status)

    def test_ansible_yaml_parses(self):
        paths = sorted((ROOT / "ansible").rglob("*.yml"))
        self.assertGreater(len(paths), 0)
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertIsNotNone(yaml.safe_load(path.read_text()))

    def test_catalog_references_only_named_secret_handles(self):
        for ref in self.catalog["applications"]:
            entry = load_json(f"catalog/v1/{ref['path']}")
            for secret in entry.get("secret_references", []):
                self.assertNotIn("=", secret)
                self.assertNotIn(" ", secret)


if __name__ == "__main__":
    unittest.main()
