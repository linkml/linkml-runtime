import re
import logging
from unittest import TestCase, main
from linkml_runtime.utils.schemaview import SchemaView
from tests.test_issues.environment import env

class TestLinkmlIssue497(TestCase):
   env = env

   def test_linkml_issue_497(self):
      
      view = SchemaView(env.input_path('linkml_issue_497.yaml'))
      biosample_processing = view.get_class('biosample processing')
      omics_processing = view.get_class('omics processing')

      has_input = view.get_slot('has input')
      has_input_bp = view.induced_slot('has input', 'biosample processing')
      has_input_op = view.induced_slot('has input', 'omics processing')

      # testing schemaview ranges
      assert has_input.range == 'named thing'
      assert has_input_bp.range == 'biosample'
      assert has_input_op.range == 'biosample'

      # test python file's has_input attribute
      with open(env.input_path('linkml_issue_497.py')) as f:
        for line in f:
            if re.match(r'\s*has_input.*NamedThing.*', line):
               logging.error('has_input range is NamedThing.', line.strip())
               assert False


if __name__ == "__main__":
   main()
