import unittest
from contextlib import redirect_stderr
from io import StringIO

from rdflib import URIRef

from linkml_runtime.utils.curienamespace import CurieNamespace
from tests.support.test_environment import TestEnvironmentTestCase

model = schema_str = """
id: http://example.org
name: inline-dict-test
imports:
  - https://w3id.org/linkml/types
# prefixes:
#   x: http://example.org/
# default_prefix: x
default_range: string
description: test

classes:
  NamedThing:
    slots:
      - id
      - full_name
      - thingtype
  Person:
    is_a: NamedThing
    class_uri: "http://testbreaker/not-the-uri-you-expect"
    slots:
      - height
  Organisation:
    is_a: NamedThing
    slots:
      - number_of_employees
  NonProfit:
    is_a: Organisation
  ForProfit:
    is_a: Organisation
    slots:
      - target_profit_margin
  Container:
    tree_root: true
    slots:
      - things
  ContainerWithOneSibling:
    slots:
      - persons
slots:
  id:
    identifier: true
    range: string
    required: true
  thingtype:
    designates_type: true
    range: uriorcurie
  full_name:
    range: string
  target_profit_margin:
    range: float
  height:
    range: integer
  number_of_employees:
    range: integer
  things:
    range: NamedThing
    multivalued: true
    inlined_as_list: true
  persons:
    range: Person
    multivalued: true
    inlined_as_list: true
"""



class CurieNamespaceTestCase(unittest.TestCase):
    def test_basics(self):
        BFO = CurieNamespace('bfo', "http://purl.obolibrary.org/obo/BFO_")
        self.assertEqual(URIRef("http://purl.obolibrary.org/obo/BFO_test"), BFO.test)
        self.assertEqual("http://purl.obolibrary.org/obo/BFO_", BFO)
        self.assertEqual("bfo:test", BFO.curie('test'))
        self.assertEqual("bfo:", BFO.curie())

    @unittest.expectedFailure
    def test_curie_as_curie(self):
        """ "curie can't be a local name at the moment" """
        BFO = CurieNamespace('bfo', "http://purl.obolibrary.org/obo/BFO_")
        self.assertEqual("bfo:curie", BFO.curie)

    def test_curie_catalog(self):
        """ Test the CurieNamespace curie to uri and uri to curi conversions"""
        from tests.test_utils.input.CurieNamespace_test import Person, namespaceCatalog
        # Make sure the import doesn't get factored out
        Person(id="Fred")

        # Test bidirectional conversion
        CurieNamespace("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#").addTo(namespaceCatalog)
        self.assertEqual('rdf:chaos',
                         namespaceCatalog.to_curie('http://www.w3.org/1999/02/22-rdf-syntax-ns#chaos'))
        self.assertEqual(URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#penguins'),
                         namespaceCatalog.to_uri('rdf:penguins'))

        # Test missing URI and CURIE
        self.assertIsNone(namespaceCatalog.to_curie('http://nothing.org/never'))
        self.assertIsNone(namespaceCatalog.to_uri('abcd:efgh'))

        # Test the default namespace
        self.assertEqual('http://example.org/ttfn', str(namespaceCatalog.to_uri(':ttfn')))
        self.assertEqual(':foul_soap', str(namespaceCatalog.to_curie('http://example.org/foul_soap')))

        # Make sure we pick the longest path
        self.assertEqual(':inst#probe', namespaceCatalog.to_curie(URIRef('http://example.org/inst#probe')))
        CurieNamespace('long_ex', 'http://example.org/inst#').addTo(namespaceCatalog)
        self.assertEqual('long_ex:probe', namespaceCatalog.to_curie(URIRef('http://example.org/inst#probe')))

        # Test incremental add
        CurieNamespace('tester', URIRef('http://fester.bester/tester#')).addTo(namespaceCatalog)
        self.assertEqual('tester:hip_boots', namespaceCatalog.to_curie('http://fester.bester/tester#hip_boots'))

        # Test multiple prefixes for same suffix
        CurieNamespace('ns17', URIRef('http://fester.bester/tester#')).addTo(namespaceCatalog)
        self.assertEqual('tester:hip_boots', namespaceCatalog.to_curie('http://fester.bester/tester#hip_boots'))
        self.assertEqual('http://fester.bester/tester#hip_boots', str(namespaceCatalog.to_uri('tester:hip_boots')))
        self.assertEqual('http://fester.bester/tester#hip_boots', str(namespaceCatalog.to_uri('ns17:hip_boots')))

        # Test multiple uris for same prefix
        # The following should be benign
        CurieNamespace('tester', URIRef('http://fester.bester/tester#')).addTo(namespaceCatalog)

        # Issue warnings for now on this
        # TODO: test that we log the following
        #       'Prefix: tester already references http://fester.bester/tester# -
        #       not updated to http://fester.notsogood/tester#'
        CurieNamespace('tester', URIRef('http://fester.notsogood/tester#')).addTo(namespaceCatalog)



if __name__ == '__main__':
    unittest.main()
