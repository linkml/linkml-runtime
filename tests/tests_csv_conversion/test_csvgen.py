import os
import unittest
import json

from linkml_runtime.dumpers import json_dumper, rdf_dumper
from linkml_runtime.loaders import yaml_loader
from linkml.generators.yamlgen import YAMLGenerator
from tests.test_models.books_normalized import *
from linkml_solr.utils.csv_dumper import CSVDumper, CSVLoader

csv_dumper = CSVDumper()
csv_loader = CSVLoader()

from tests import INPUT_DIR, MODEL_DIR, OUTPUT_DIR

SCHEMA = os.path.join(MODEL_DIR, 'books_normalized.yaml')
DATA = os.path.join(INPUT_DIR, 'books_normalized_01.yaml')
DATA2 = os.path.join(INPUT_DIR, 'books_normalized_02.yaml')
OUTPUT = os.path.join(OUTPUT_DIR, 'books_flattened.tsv')
OUTPUT2 = os.path.join(OUTPUT_DIR, 'books_flattened_02.tsv')

def _json(obj) -> str:
    return json.dumps(obj, indent=' ', sort_keys=True)

class CSVGenTestCase(unittest.TestCase):

    def test_csvgen_roundtrip(self):
        schema = YAMLGenerator(SCHEMA).schema
        data = yaml_loader.load(DATA, target_class=Shop)
        #print(json_dumper.dumps(data))
        #print(csv_dumper.dumps(data, index_slot='all_book_series', schema=schema))
        csv_dumper.dump(data, to_file=OUTPUT, index_slot='all_book_series', schema=schema)
        roundtrip = csv_loader.load(OUTPUT, target_class=Shop, index_slot='all_book_series', schema=schema)
        print(json_dumper.dumps(roundtrip))
        assert roundtrip == data

    def test_csvgen_unroundtrippable(self):
        schema = YAMLGenerator(SCHEMA).schema
        data = yaml_loader.load(DATA2, target_class=Shop)
        #print(json_dumper.dumps(data))
        #print(csv_dumper.dumps(data, index_slot='all_book_series', schema=schema))
        csv_dumper.dump(data, to_file=OUTPUT2, index_slot='all_book_series', schema=schema)
        roundtrip = csv_loader.load(OUTPUT2, target_class=Shop, index_slot='all_book_series', schema=schema)
        print(json_dumper.dumps(roundtrip))
        #assert roundtrip == data







if __name__ == '__main__':
    unittest.main()
