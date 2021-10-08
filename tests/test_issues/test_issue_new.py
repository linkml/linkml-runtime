import unittest

import yaml
import io

from tests.test_issues.input.kitchen_sink import Dataset
from linkml_runtime.loaders import yaml_loader

inp_yaml = """
---
companies:
  - id: 201
    name: 'Aperture Science'
    value:
      - value: 104.41
      - value: 199.41
    ceo: 
      - id: 1001
        name: Cave Johnson
        has employment history:
          - ended at time: 2000-12-31
            started at time: 1999-11-20
          - ended at time: 2001-03-03
            started at time: 2001-01-01
      - id: 1002
        name: Cave Johnson
        has employment history:
          - ended at time: 2000-12-31
            started at time: 1999-11-20
          - ended at time: 2001-03-03
            started at time: 2001-01-01
          
  - id: 202
    name: 'Goliath Corporation'
"""


class IssueNewTestCase(unittest.TestCase):
    def test_import(self):
        yaml_obj_list = yaml.load_all(io.StringIO(inp_yaml), Loader=yaml.FullLoader)
        for yaml_obj in yaml_obj_list:
            dataset = yaml_loader.load(yaml_obj, Dataset)
            print(dataset['companies'])
