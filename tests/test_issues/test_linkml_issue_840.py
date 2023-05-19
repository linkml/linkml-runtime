import unittest

from linkml_runtime.utils.schemaview import SchemaView

from tests.test_issues.environment import env

SCHEMA = env.input_path("linkml_issue_840.yaml")


class Issue840TestCase(unittest.TestCase):
    env = env

    def test_issue_840(self):
        """schema_map attribute of SchemaView()"""
        sv = SchemaView(SCHEMA)

        # make call to imports_closure() method
        # which returns all imports
        sv.imports_closure()
        actual_result = list(sv.schema_map.keys())

        expected_result = ["issue-840", "issue-840-import"]

        self.assertListEqual(actual_result, expected_result)


if __name__ == "__main__":
    unittest.main()
