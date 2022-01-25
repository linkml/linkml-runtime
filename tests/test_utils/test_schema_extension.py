import os
import unittest
import logging
from copy import copy

from linkml_runtime.linkml_model.meta import SchemaDefinition, ClassDefinition, SlotDefinitionName, SlotDefinition
from linkml_runtime.loaders.yaml_loader import YAMLLoader
from linkml_runtime.utils.schemaview import SchemaView, SchemaUsage
from linkml_runtime.utils.schemaops import roll_up, roll_down
from tests.test_utils import INPUT_DIR
from tests.test_utils.model.schema_extension import ExtSchema, ExtClass

SCHEMA = os.path.join(INPUT_DIR, 'schema_extension_example.yaml')

yaml_loader = YAMLLoader()

class SchemaExtensionTestCase(unittest.TestCase):
    """
    Tests the experimental ability to extend the metamodel

    To extend the metamodel make extensions of all required metamodel classes;
    make sure you narrow the range of metaslots using slot_usage:

    .. code:: yaml

      ExtSchema:
        is_a: schema_definition
        slot_usage:
          classes:
            range: ExtClass
          slots:
            range: ExtSlot

      ExtClass:
        is_a: class_definition
        slots:
          - ext_info

      ExtSlot:
        is_a: slot_definition
        slots:
          - ext_info

    After this, compile to python as if it were any other schema



    """

    def test_schema_extension(self):
        # no import schema
        view = SchemaView(SCHEMA, schema_instantiates=ExtSchema)
        my_class = view.get_class('MyClass')
        self.assertIsInstance(my_class, ExtClass)
        self.assertEqual(my_class.ext_info, 'my ext info here')
        for cn, c in view.all_classes().items():
            if not isinstance(c, ExtClass):
                raise ValueError(f'{cn} not an ext')




if __name__ == '__main__':
    unittest.main()
