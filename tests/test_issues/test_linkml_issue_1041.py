from unittest import TestCase

from rdflib import RDF, URIRef

from linkml_runtime.dumpers import rdflib_dumper
from linkml_runtime.utils.schemaview import SchemaView

from tests.test_issues.environment import env
from tests.test_issues.models.linkml_issue_1041 import Person


class Issue1041TestCase(TestCase):
    """
    https://github.com/linkml/linkml/issues/1041
    """
    env = env

    def test_issue_default_prefix(self):
        view = SchemaView(env.input_path('linkml_issue_1041.yaml'))
        uri = view.get_uri(view.get_class("Person"), expand=True)
        person_uri = "https://w3id.org/linkml/examples/personinfo/Person"
        self.assertEqual(uri, person_uri)
        p = Person(id="ORCID:1234", full_name="Clark Kent", age="32", phone="555-555-5555")
        g = rdflib_dumper.as_rdf_graph(p, view)
        bnodes = g.subjects(RDF.type, URIRef(person_uri))
        self.assertEqual(1, len(list(bnodes)))


if __name__ == "__main__":
    unittest.main()
