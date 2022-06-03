import os
import unittest
from rdflib import Graph
from linkml_runtime.dumpers import rdflib_dumper
from linkml_runtime.loaders import yaml_loader
from linkml_runtime.utils.schemaview import SchemaView
from tests.test_loaders_dumpers import INPUT_DIR, OUTPUT_DIR
from tests.test_loaders_dumpers.models.issue_429_schema import Container

SCHEMA = os.path.join(INPUT_DIR, 'issue_429_schema.yaml')
DATA = os.path.join(INPUT_DIR, 'issue_429_data.yaml')
OUT = os.path.join(OUTPUT_DIR, 'issue_429_data.ttl')


class RdfLibDumperTestCase(unittest.TestCase):

    def test_rdflib_dumper(self):
        view = SchemaView(SCHEMA)
        container = yaml_loader.load(DATA, target_class=Container)
        rdflib_dumper.dump(container, schemaview=view, to_file=OUT)
        g = Graph()
        g.parse(OUT, format='ttl')


if __name__ == '__main__':
    unittest.main()
