import os
import json
from datetime import date
from linkml_runtime.dumpers import rdf_dumper, rdflib_dumper
from linkml_runtime.utils.schemaview import SchemaView
from tests.test_loaders_dumpers.models.personinfo_pydantic import EmploymentEvent, Person, Organization
from tests.test_loaders_dumpers.loaderdumpertestcase import LoaderDumperTestCase

class PydanticDumpersTestCase(LoaderDumperTestCase):

    @classmethod
    def get_schema_path(cls):
        current_dir = os.path.dirname(__file__)
        return os.path.join(current_dir, "input", "example_personinfo.yaml")

    @classmethod
    def get_context(cls):
        current_dir = os.path.dirname(__file__)
        return os.path.join(current_dir, "input", "example_personinfo.context.jsonld")

    @classmethod
    def setUpClass(cls) -> None:
        LoaderDumperTestCase.setUpClass()
        org_w = Organization(id="WIDG:001", name="Widget Corp", description="A company that makes widgets")
        org_g = Organization(id="GIDG:001", name="Gadget Corp", description="A company that makes gadgets")
        employment = [
            EmploymentEvent(
                employed_at=org_w.id,
                started_at_time=date(2020, 1, 1),
                ended_at_time=date(2021, 1, 1),
            ),
            EmploymentEvent(
                employed_at=org_g.id,
                started_at_time=date(2021, 2, 1),
                is_current=True,
                ended_at_time=None,
            ),
        ]
        cls.person = Person(id="P:001", name="Alice Smith", has_employment_history=employment)
        cls.schemaview = SchemaView(cls.get_schema_path())
        cls.context = cls.get_context()

    def test_rdf_dumper(self):
        """Test serialization with rdf_dumper"""
        rdf_str = rdf_dumper.dumps(self.person, contexts=self.context)
        self.assertIsInstance(rdf_str, str)
        self.assertTrue(len(rdf_str) > 0)
        self.assertIn("Alice Smith", rdf_str)

    def test_rdflib_dumper(self):
        """Test serialization with rdflib_dumper"""
        rdf_str = rdflib_dumper.dumps(self.person, schemaview=self.schemaview)
        self.assertIsInstance(rdf_str, str)
        self.assertTrue(len(rdf_str) > 0)
