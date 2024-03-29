import unittest

import yaml

from linkml_runtime.utils.yamlutils import DupCheckYamlLoader
from tests.support.test_environment import TestEnvironmentTestCase
from tests.test_utils.environment import env


class YamlUtilTestCase(TestEnvironmentTestCase):
    env = env

    def test_dupcheck_loader(self):
        """ Make sure the duplicate checker finds duplicates """
        with open(env.input_path('yaml1.yaml')) as f:
            y1 = yaml.safe_load(f)
            self.assertEqual(17, y1['f1'])
        with open(env.input_path('yaml1.yaml')) as f:
            with self.assertRaises(ValueError):
                yaml.load(f, DupCheckYamlLoader)
        with open(env.input_path('yaml2.yaml')) as f:
            with self.assertRaises(ValueError):
                yaml.load(f, DupCheckYamlLoader)
        with open(env.input_path('schema1.yaml')) as f:
            s1 = yaml.load(f, DupCheckYamlLoader)
            self.assertEqual('schema1', s1['name'])

    def test_line_numbers(self):
        s = """
        name: schema1
        info: foo
        x:
           a: 1
           b: 2
        l: [1, 2, 3]
        """
        obj = yaml.load(s, DupCheckYamlLoader)
        cases = [
            ('name', 1),
            ('info', 2),
            ('x', 3),
            ('l', 6),
        ]
        key_to_lines = [(k, k._s.line) for k in obj.keys()]
        self.assertCountEqual(cases, key_to_lines)




if __name__ == '__main__':
    unittest.main()
