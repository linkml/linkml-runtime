import os
import unittest
import logging
from copy import copy
from pathlib import Path
from typing import List
import pytest 
from unittest import TestCase

from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.linkml_model.meta import SchemaDefinition, ClassDefinition, SlotDefinitionName, SlotDefinition, \
    ClassDefinitionName, Prefix
from linkml_runtime.loaders.yaml_loader import YAMLLoader
from linkml_runtime.utils.introspection import package_schemaview
from linkml_runtime.utils.schemaview import SchemaView, SchemaUsage, OrderedBy
from linkml_runtime.utils.schemaops import roll_up, roll_down
from tests.test_utils import INPUT_DIR

SCHEMA_NO_IMPORTS = Path(INPUT_DIR) / 'kitchen_sink_noimports.yaml'
SCHEMA_WITH_IMPORTS = Path(INPUT_DIR) / 'kitchen_sink.yaml'
SCHEMA_WITH_STRUCTURED_PATTERNS = Path(INPUT_DIR) / "pattern-example.yaml"
SCHEMA_IMPORT_TREE = Path(INPUT_DIR) / 'imports' / 'main.yaml'

yaml_loader = YAMLLoader()
IS_CURRENT = 'is current'
EMPLOYED_AT = 'employed at'
COMPANY = 'Company'
AGENT = 'agent'
ACTIVITY = 'activity'
RELATED_TO = 'related to'
AGE_IN_YEARS = 'age in years'


def test_induced_range():
    view = SchemaView(SCHEMA_WITH_IMPORTS)
    rangers = view.induced_slot('related to', 'Alien').range_expression
    print("class name: Alien")
    if rangers:
        for ranger in rangers:
            print(ranger.name)
    rangers = view.induced_slot('related to', 'Person').range_expression
    print("class name: Person")
    if rangers:
        for ranger in rangers:
            print(ranger.name)
    else:
        print(view.induced_slot('related to', 'Person').range)
    print("class name: FamilialRelationship")
    rangers = view.induced_slot('related to', 'FamilialRelationship').range_expression
    if rangers:
        for ranger in rangers:
            print(ranger.name)
    else:
        print(view.induced_slot('related to', 'FamilialRelationship').range)


def test_children_method():
    view = SchemaView(SCHEMA_NO_IMPORTS)
    children = view.get_children("Person")
    assert children == ['Adult']


def test_all_aliases():
    """
    This tests the aliases slot (not: alias)
    :return:
    """
    view = SchemaView(SCHEMA_NO_IMPORTS)
    aliases = view.all_aliases()
    assert "identifier" in aliases["id"]
    assert "A" in aliases["subset A"]
    assert "B" in aliases["subset B"]
    assert "dad" in aliases["Adult"]
    assert "test" not in aliases["Adult"]


def test_alias_slot():
    """
    Tests the alias slot.

    The induced slot alias should always be populated. For induced slots, it should default to the
    name field if not present.
    """
    view = SchemaView(SCHEMA_NO_IMPORTS)
    for c in view.all_classes().values():
        for s in view.class_induced_slots(c.name):
            assert s.alias is not None
    postal_code_slot = view.induced_slot('postal code', 'Address')
    assert postal_code_slot.name == 'postal code'
    assert postal_code_slot.alias == 'zip'


def test_schemaview_enums():
    view = SchemaView(SCHEMA_NO_IMPORTS)
    with pytest.raises(ValueError):
        view.permissible_value_parent("not_a_pv", "not_an_enum")
    for en, e in view.all_enums().items():
        if e.name == "Animals":
            for pv, v in e.permissible_values.items():
                if pv == "CAT":
                    assert view.permissible_value_parent(pv, e.name) is None
                    assert view.permissible_value_ancestors(pv, e.name) == ['CAT']
                    assert "LION" in view.permissible_value_descendants(pv, e.name)
                    assert "ANGRY_LION" in view.permissible_value_descendants(pv, e.name)
                    assert "TABBY" in view.permissible_value_descendants(pv, e.name)
                    assert "EAGLE" not in view.permissible_value_descendants(pv, e.name)

                    assert "TABBY" in view.permissible_value_children(pv, e.name)
                    assert "LION" in view.permissible_value_children(pv, e.name)

                if pv == "LION":
                    assert "ANGRY_LION" in view.permissible_value_children(pv, e.name)
                if pv == "ANGRY_LION":
                    assert view.permissible_value_parent(pv, e.name) == ['LION']
                    assert view.permissible_value_ancestors(pv, e.name) == ['ANGRY_LION', 'LION', 'CAT']
                    assert ["ANGRY_LION"] == view.permissible_value_descendants(pv, e.name)
        for cn, c in view.all_classes().items():
            if c.name == "Adult":
                assert view.class_ancestors(c.name) == ['Adult', 'Person', 'HasAliases', 'Thing']


def test_schemaview():
    # no import schema
    view = SchemaView(SCHEMA_NO_IMPORTS)
    logging.debug(view.imports_closure())
    assert len(view.imports_closure()) == 1
    all_cls = view.all_classes()
    logging.debug(f'n_cls = {len(all_cls)}')

    assert list(view.annotation_dict(IS_CURRENT).values()) == ['bar']
    logging.debug(view.annotation_dict(EMPLOYED_AT))
    e = view.get_element(EMPLOYED_AT)
    logging.debug(e.annotations)
    e = view.get_element('has employment history')
    logging.debug(e.annotations)

    elements = view.get_elements_applicable_by_identifier("ORCID:1234")
    assert "Person" in elements
    elements = view.get_elements_applicable_by_identifier("PMID:1234")
    assert "Organization" in elements
    elements = view.get_elements_applicable_by_identifier("http://www.ncbi.nlm.nih.gov/pubmed/1234")
    assert "Organization" in elements
    elements = view.get_elements_applicable_by_identifier("TEST:1234")
    assert "anatomical entity" not in elements
    assert list(view.annotation_dict(SlotDefinitionName(IS_CURRENT)).values()) == ['bar']
    logging.debug(view.annotation_dict(SlotDefinitionName(EMPLOYED_AT)))
    element = view.get_element(SlotDefinitionName(EMPLOYED_AT))
    logging.debug(element.annotations)
    element = view.get_element(SlotDefinitionName('has employment history'))
    logging.debug(element.annotations)

    assert view.is_mixin('WithLocation')
    assert not view.is_mixin('BirthEvent')

    assert view.inverse('employment history of') == 'has employment history'
    assert view.inverse('has employment history') == 'employment history of'

    mapping = view.get_mapping_index()
    assert mapping is not None

    category_mapping = view.get_element_by_mapping("GO:0005198")
    assert category_mapping == [ACTIVITY]

    assert view.is_multivalued('aliases')
    assert not view.is_multivalued('id')
    assert view.is_multivalued('dog addresses')

    assert view.slot_is_true_for_metadata_property('aliases', 'multivalued')
    assert view.slot_is_true_for_metadata_property('id', 'identifier')
    with pytest.raises(ValueError):
        view.slot_is_true_for_metadata_property('aliases', 'aliases')

    for tn, t in view.all_types().items():
        logging.info(f'TN = {tn}')
        assert 'https://w3id.org/linkml/tests/kitchen_sink' == t.from_schema
    for sn, s in view.all_slots().items():
        logging.info(f'SN = {sn} RANGE={s.range}')
        assert 'https://w3id.org/linkml/tests/kitchen_sink' == s.from_schema
        # range should always be populated: See https://github.com/linkml/linkml/issues/733
        rng = view.induced_slot(sn).range
        assert rng is not None
    # this section is mostly for debugging
    for cn in all_cls.keys():
        c = view.get_class(cn)
        assert 'https://w3id.org/linkml/tests/kitchen_sink' == c.from_schema
        logging.debug(f'{cn} PARENTS = {view.class_parents(cn)}')
        logging.debug(f'{cn} ANCS = {view.class_ancestors(cn)}')
        logging.debug(f'{cn} CHILDREN = {view.class_children(cn)}')
        logging.debug(f'{cn} DESCS = {view.class_descendants(cn)}')
        logging.debug(f'{cn} SCHEMA = {view.in_schema(cn)}')
        logging.debug(f'  SLOTS = {view.class_slots(cn)}')
        for sn in view.class_slots(cn):
            slot = view.get_slot(sn)
            assert 'https://w3id.org/linkml/tests/kitchen_sink' == slot.from_schema
            logging.debug(f'  SLOT {sn} R: {slot.range} U: {view.get_uri(sn)} ANCS: {view.slot_ancestors(sn)}')
            induced_slot = view.induced_slot(sn, cn)
            logging.debug(f'    INDUCED {sn}={induced_slot}')
            # range should always be populated: See https://github.com/linkml/linkml/issues/733
            assert induced_slot.range is not None

    logging.debug(f'ALL = {view.all_elements().keys()}')

    # -- TEST ANCESTOR/DESCENDANTS FUNCTIONS --
    assert sorted(['Company', 'Organization', 'HasAliases', 'Thing']) == sorted(view.class_ancestors(COMPANY))
    assert sorted(['Organization', 'HasAliases', 'Thing']) == sorted(view.class_ancestors(COMPANY, reflexive=False))
    assert sorted(['Thing', 'Person', 'Organization', COMPANY, 'Adult']) == sorted(view.class_descendants('Thing'))

    # -- TEST CLASS SLOTS --

    assert sorted(['id', 'name',  # From Thing
                   'has employment history', 'has familial relationships', 'has medical history',
                   AGE_IN_YEARS, 'addresses', 'has birth event', 'reason_for_happiness',  # From Person
                   'aliases'  # From HasAliases
                   ]) == sorted(view.class_slots('Person'))
    assert sorted(view.class_slots('Person')) == sorted(view.class_slots('Adult'))
    assert sorted(['id', 'name',  # From Thing
                   'ceo',  # From COMPANY
                   'aliases'  # From HasAliases
                   ]) == sorted(view.class_slots(COMPANY))

    assert view.get_class(AGENT).class_uri == 'prov:Agent'
    assert view.get_uri(AGENT) == 'prov:Agent'
    logging.debug(view.get_class(COMPANY).class_uri)

    assert view.get_uri(COMPANY) == 'ks:Company'
    # test induced slots

    for c in [COMPANY, 'Person', 'Organization']:
        islot = view.induced_slot('aliases', c)
        assert islot.multivalued is True
        assert islot.owner == c, 'owner does not match'
        assert view.get_uri(islot, expand=True) == 'https://w3id.org/linkml/tests/kitchen_sink/aliases'

    assert view.get_identifier_slot('Company').name == 'id'
    assert view.get_identifier_slot('Thing').name == 'id'
    assert view.get_identifier_slot('FamilialRelationship') is None
    for c in [COMPANY, 'Person', 'Organization', 'Thing']:
        assert view.induced_slot('id', c).identifier is True
        assert not view.induced_slot('name', c).identifier
        assert not view.induced_slot('name', c).required
        assert view.induced_slot('name', c).range == 'string'
        assert view.induced_slot('id', c).owner == c, 'owner does not match'
        assert view.induced_slot('name', c).owner == c, 'owner does not match'
    for c in ['Event', 'EmploymentEvent', 'MedicalEvent']:
        s = view.induced_slot('started at time', c)
        logging.debug(f's={s.range} // c = {c}')
        assert s.range == 'date'
        assert s.slot_uri == 'prov:startedAtTime'
        assert s.owner == c, 'owner does not match'
        c_induced = view.induced_class(c)
        # an induced class should have no slots
        assert c_induced.slots == []
        assert c_induced.attributes != []
        s2 = c_induced.attributes['started at time']
        assert s2.range == 'date'
        assert s2.slot_uri == 'prov:startedAtTime'

    # test slot_usage
    assert view.induced_slot(AGE_IN_YEARS, 'Person').minimum_value == 0
    assert view.induced_slot(AGE_IN_YEARS, 'Adult').minimum_value == 16
    assert view.induced_slot('name', 'Person').pattern is not None
    assert view.induced_slot('type', 'FamilialRelationship').range == 'FamilialRelationshipType'
    assert view.induced_slot(RELATED_TO, 'FamilialRelationship').range == 'Person'
    assert view.get_slot(RELATED_TO).range == 'Thing'
    assert view.induced_slot(RELATED_TO, 'Relationship').range == 'Thing'
    # https://github.com/linkml/linkml/issues/875
    assert sorted(['Thing', 'Place']) == sorted(view.induced_slot('name').domain_of)

    a = view.get_class(ACTIVITY)
    assert sorted(a.exact_mappings) == sorted(['prov:Activity'])
    logging.debug(view.get_mappings(ACTIVITY, expand=True))
    assert sorted(view.get_mappings(ACTIVITY)['exact']) == sorted(['prov:Activity'])
    assert sorted(view.get_mappings(ACTIVITY, expand=True)['exact']) == sorted(['http://www.w3.org/ns/prov#Activity'])

    u = view.usage_index()
    for k, v in u.items():
        logging.debug(f' {k} = {v}')
    assert SchemaUsage(used_by='FamilialRelationship', slot=RELATED_TO, metaslot='range', used='Person',
                       inferred=False) in u['Person']

    u = view.usage_index()

    expected_marriage_event = [
        ('Person', 'reason_for_happiness', 'any_of[range]', 'MarriageEvent', True),
        ('Adult', 'reason_for_happiness', 'any_of[range]', 'MarriageEvent', False)
    ]

    actual_marriage_event = [
        (su.used_by, su.slot, su.metaslot, su.used, su.inferred)
        for su in u['MarriageEvent']
    ]

    assert sorted(actual_marriage_event) == sorted(expected_marriage_event)

    expected_employment_event = [
        ('Person', 'has employment history', 'range', 'EmploymentEvent', True),
        ('Person', 'reason_for_happiness', 'any_of[range]', 'EmploymentEvent', True),
        ('Adult', 'has employment history', 'range', 'EmploymentEvent', False),
        ('Adult', 'reason_for_happiness', 'any_of[range]', 'EmploymentEvent', False)
    ]

    actual_employment_event = [
        (su.used_by, su.slot, su.metaslot, su.used, su.inferred)
        for su in u['EmploymentEvent']
    ]

    assert sorted(actual_employment_event) == sorted(expected_employment_event)

    # test methods also work for attributes
    leaves = view.class_leaves()
    logging.debug(f'LEAVES={leaves}')
    assert 'MedicalEvent' in leaves
    roots = view.class_roots()
    logging.debug(f'ROOTS={roots}')
    assert 'Dataset' in roots
    ds_slots = view.class_slots('Dataset')
    logging.debug(ds_slots)
    assert len(ds_slots) == 3
    assert sorted(['persons', 'companies', 'activities']) == sorted(ds_slots)
    for sn in ds_slots:
        s = view.induced_slot(sn, 'Dataset')
        logging.debug(s)


def test_all_classes_ordered_lexical():
    view = SchemaView(SCHEMA_NO_IMPORTS)
    classes = view.all_classes(ordered_by=OrderedBy.LEXICAL)

    ordered_c = []
    for c in classes.values():
        ordered_c.append(c.name)
    assert ordered_c == sorted(ordered_c)


def test_all_classes_ordered_rank():
    view = SchemaView(SCHEMA_NO_IMPORTS)
    classes = view.all_classes(ordered_by=OrderedBy.RANK)
    ordered_c = []
    for c in classes.values():
        ordered_c.append(c.name)
    first_in_line = []
    second_in_line = []
    for name, definition in classes.items():
        if definition.rank == 1:
            first_in_line.append(name)
        elif definition.rank == 2:
            second_in_line.append(name)
    assert ordered_c[0] in first_in_line
    assert ordered_c[10] not in second_in_line


def test_all_classes_ordered_no_ordered_by():
    view = SchemaView(SCHEMA_NO_IMPORTS)
    classes = view.all_classes()
    ordered_c = [c.name for c in classes.values()]
    assert ordered_c[0] == "HasAliases"
    assert ordered_c[-1] == "EmptyClass"
    assert ordered_c[-2] == "agent"


def test_all_slots_ordered_lexical():
    view = SchemaView(SCHEMA_NO_IMPORTS)
    slots = view.all_slots(ordered_by=OrderedBy.LEXICAL)
    ordered_s = []
    for s in slots.values():
        ordered_s.append(s.name)
    assert ordered_s == sorted(ordered_s)


def test_all_slots_ordered_rank():
    view = SchemaView(SCHEMA_NO_IMPORTS)
    slots = view.all_slots(ordered_by=OrderedBy.RANK)
    ordered_s = []
    for s in slots.values():
        ordered_s.append(s.name)
    first_in_line = []
    second_in_line = []
    for name, definition in slots.items():
        if definition.rank == 1:
            first_in_line.append(name)
        elif definition.rank == 2:
            second_in_line.append(name)
    assert ordered_s[0] in first_in_line
    assert ordered_s[10] not in second_in_line


def test_rollup_rolldown():
    # no import schema
    view = SchemaView(SCHEMA_NO_IMPORTS)
    element_name = 'Event'
    roll_up(view, element_name)
    for slot in view.class_induced_slots(element_name):
        logging.error(slot)
    induced_slot_names = [s.name for s in view.class_induced_slots(element_name)]
    logging.error(induced_slot_names)
    assert sorted(['started at time', 'ended at time', IS_CURRENT, 'in location', EMPLOYED_AT, 'married to']) == sorted(
        induced_slot_names)

    # check to make sure rolled-up classes are deleted
    assert view.class_descendants(element_name, reflexive=False) == []
    roll_down(view, view.class_leaves())

    for element_name in view.all_classes():
        c = view.get_class(element_name)
        logging.debug(f'{element_name}')
        logging.debug(f'  {element_name} SLOTS(i) = {view.class_slots(element_name)}')
        logging.debug(f'  {element_name} SLOTS(d) = {view.class_slots(element_name, direct=True)}')
        assert sorted(view.class_slots(element_name)) == sorted(view.class_slots(element_name, direct=True))

    assert 'Thing' not in view.all_classes()
    assert 'Person' not in view.all_classes()
    assert 'Adult' in view.all_classes()

def test_caching():
    """
    Determine if cache is reset after modifications made to schema
    """
    schema = SchemaDefinition(id='test', name='test')
    view = SchemaView(schema)
    assert sorted([]) == sorted(view.all_classes())
    view.add_class(ClassDefinition('X'))
    assert sorted(['X']) == sorted(view.all_classes())
    view.add_class(ClassDefinition('Y'))
    assert sorted(['X', 'Y']) == sorted(view.all_classes())
    # bypass view method and add directly to schema;
    # in general this is not recommended as the cache will
    # not be updated
    view.schema.classes['Z'] = ClassDefinition('Z')
    # as expected, the view doesn't know about Z
    assert sorted(['X', 'Y']) == sorted(view.all_classes())
    # inform the view modifications have been made
    view.set_modified()
    # should be in sync
    assert sorted(['X', 'Y', 'Z']) == sorted(view.all_classes())
    # recommended way to make updates
    view.delete_class('X')
    # cache will be up to date
    assert sorted(['Y', 'Z']) == sorted(view.all_classes())
    view.add_class(ClassDefinition('W'))
    assert sorted(['Y', 'Z', 'W']) == sorted(view.all_classes())


def test_import_map():
    """
    Path to import file should be configurable
    """
    for im in [{"core": "/no/such/file"}, {"linkml:": "/no/such/file"}]:
        with pytest.raises(FileNotFoundError):
            view = SchemaView(SCHEMA_WITH_IMPORTS, importmap=im)
            view.all_classes()
    for im in [None, {}, {"core": "core"}]:
        view = SchemaView(SCHEMA_WITH_IMPORTS, importmap=im)
        view.all_classes()
        assert sorted(['kitchen_sink', 'core', 'linkml:types']) == sorted(view.imports_closure())
        assert ACTIVITY in view.all_classes()
        assert ACTIVITY not in view.all_classes(imports=False)


def test_imports():
    """
    view should by default dynamically include imports chain
    """
    view = SchemaView(SCHEMA_WITH_IMPORTS)
    assert view.schema.source_file is not None
    logging.debug(view.imports_closure())
    assert sorted(['kitchen_sink', 'core', 'linkml:types']) == sorted(view.imports_closure())
    for t in view.all_types().keys():
        logging.debug(f'T={t} in={view.in_schema(t)}')
    assert view.in_schema(ClassDefinitionName('Person')) == 'kitchen_sink'
    assert view.in_schema(SlotDefinitionName('id')) == 'core'
    assert view.in_schema(SlotDefinitionName('name')) == 'core'
    assert view.in_schema(SlotDefinitionName(ACTIVITY)) == 'core'
    assert view.in_schema(SlotDefinitionName('string')) == 'types'
    assert ACTIVITY in view.all_classes()
    assert ACTIVITY not in view.all_classes(imports=False)
    assert 'string' in view.all_types()
    assert 'string' not in view.all_types(imports=False)
    assert sorted(['SymbolString', 'string']) == sorted(view.type_ancestors('SymbolString'))

    for tn, t in view.all_types().items():
        assert tn == t.name
        induced_t = view.induced_type(tn)
        assert induced_t.uri is not None
        # assertIsNotNone(induced_t.repr)
        assert induced_t.base is not None
        if t in view.all_types(imports=False).values():
            assert t.from_schema == 'https://w3id.org/linkml/tests/kitchen_sink'
        else:
            assert t.from_schema in ['https://w3id.org/linkml/tests/core', 'https://w3id.org/linkml/types']
    for en, e in view.all_enums().items():
        assert en == e.name
        if e in view.all_enums(imports=False).values():
            assert e.from_schema == 'https://w3id.org/linkml/tests/kitchen_sink'
        else:
            assert e.from_schema == 'https://w3id.org/linkml/tests/core'
    for sn, s in view.all_slots().items():
        assert sn == s.name
        s_induced = view.induced_slot(sn)
        assert s_induced.range is not None
        if s in view.all_slots(imports=False).values():
            assert s.from_schema == 'https://w3id.org/linkml/tests/kitchen_sink'
        else:
            assert s.from_schema == 'https://w3id.org/linkml/tests/core'
    for cn, c in view.all_classes().items():
        assert cn == c.name
        if c in view.all_classes(imports=False).values():
            assert c.from_schema == 'https://w3id.org/linkml/tests/kitchen_sink'
        else:
            assert c.from_schema == 'https://w3id.org/linkml/tests/core'
        for s in view.class_induced_slots(cn):
            if s in view.all_classes(imports=False).values():
                assert s.slot_uri is not None
                assert s.from_schema == 'https://w3id.org/linkml/tests/kitchen_sink'

    for c in ['Company', 'Person', 'Organization', 'Thing']:
        assert view.induced_slot('id', c).identifier is True
        assert not view.induced_slot('name', c).identifier
        assert not view.induced_slot('name', c).required
        assert view.induced_slot('name', c).range == 'string'
    for c in ['Event', 'EmploymentEvent', 'MedicalEvent']:
        s = view.induced_slot('started at time', c)
        assert s.range == 'date'
        assert s.slot_uri == 'prov:startedAtTime'
    assert view.induced_slot(AGE_IN_YEARS, 'Person').minimum_value == 0
    assert view.induced_slot(AGE_IN_YEARS, 'Adult').minimum_value == 16

    assert view.get_class('agent').class_uri == 'prov:Agent'
    assert view.get_uri(AGENT) == 'prov:Agent'
    logging.debug(view.get_class('Company').class_uri)

    assert view.get_uri(COMPANY) == 'ks:Company'
    assert view.get_uri(COMPANY, expand=True) == 'https://w3id.org/linkml/tests/kitchen_sink/Company'
    logging.debug(view.get_uri('TestClass'))
    assert view.get_uri('TestClass') == 'core:TestClass'
    assert view.get_uri('TestClass', expand=True) == 'https://w3id.org/linkml/tests/core/TestClass'

    assert view.get_uri('string') == 'xsd:string'

    # dynamic enums
    e = view.get_enum('HCAExample')
    assert sorted(['GO:0007049', 'GO:0022403']) == sorted(e.include[0].reachable_from.source_nodes)

    # units
    height = view.get_slot('height_in_m')
    assert height.unit.ucum_code == "m"


def test_imports_from_schemaview():
    """
    view should by default dynamically include imports chain
    """
    view = SchemaView(SCHEMA_WITH_IMPORTS)
    view2 = SchemaView(view.schema)
    assert sorted(view.all_classes()) == sorted(view2.all_classes())
    assert sorted(view.all_classes(imports=False)) == sorted(view2.all_classes(imports=False))


def test_imports_closure_order():
    """
    Imports should override in a python-like order.

    See
        - https://github.com/linkml/linkml/issues/1839 for initial discussion
        - input/imports/README.md for explanation of the test schema
    """
    sv = SchemaView(SCHEMA_IMPORT_TREE)
    closure = sv.imports_closure(imports=True)
    target = [
        'linkml:types',
        's1_1',
        's1_2_1_1_1', 's1_2_1_1_2',
        's1_2_1_1', 's1_2_1', 's1_2',
        's1',
        's2_1', 's2_2', 's2',
        's3_1', 's3_2', 's3',
        'main'
    ]
    assert closure == target


def test_imports_overrides():
    """
    Classes defined in the importing module should override same-named classes in
    imported modules.

    Tests recursively across an import tree. Each class defines all classes lower
    in the tree with a `value` attribute with an `ifabsent` value matching the
    current schema. Lower (closer to the importing schema) schemas should override
    each class at that level or lower, keeping the rest.

    See `input/imports/README.md` for further explanation.
    """
    sv = SchemaView(SCHEMA_IMPORT_TREE)
    defaults = {}
    target = {}
    for name, cls in sv.all_classes(imports=True).items():
        target[name] = name
        defaults[name] = cls.attributes['value'].ifabsent

    assert defaults == target


def test_direct_remote_imports():
    """
    Tests that building a SchemaView directly from a remote URL works.

    Note: this should be the only test in this suite that fails if there is
    no network connection.
    """
    view = SchemaView("https://w3id.org/linkml/meta.yaml")
    main_classes = ["class_definition", "prefix"]
    imported_classes = ["annotation"]
    for c in main_classes:
        assert c in view.all_classes(imports=True)
        assert c in view.all_classes(imports=False)
    for c in imported_classes:
        assert c in view.all_classes(imports=True)
        assert c not in view.all_classes(imports=False)


@pytest.mark.skip("Skipped as fragile: will break if the remote schema changes")
def test_direct_remote_imports_additional():
    """
    Alternative test to: https://github.com/linkml/linkml/pull/1379
    """
    url = "https://raw.githubusercontent.com/GenomicsStandardsConsortium/mixs/main/model/schema/mixs.yaml"
    view = SchemaView(url)
    assert view.schema.name == "MIxS"
    class_count = len(view.all_classes())
    assert class_count > 0


def test_merge_imports():
    """
    ensure merging and merging imports closure works
    """
    view = SchemaView(SCHEMA_WITH_IMPORTS)
    all_c = copy(view.all_classes())
    all_c_noi = copy(view.all_classes(imports=False))
    assert len(all_c_noi) < len(all_c)
    view.merge_imports()
    all_c2 = copy(view.all_classes())
    assert sorted(all_c) == sorted(all_c2)
    all_c2_noi = copy(view.all_classes(imports=False))
    assert len(all_c2_noi) == len(all_c2)


def test_metamodel_imports():
    """
    Tests imports of the metamodel.

    Note: this test and others should be able to run without network connectivity.
    SchemaView should make use of the version of the metamodel distributed with the package
    over the network available version.

    TODO: use mock testing framework to emulate no access to network.

    - `<https://github.com/linkml/linkml/issues/502>`_
    :return:
    """
    schema = SchemaDefinition(id='test', name='metamodel-imports-test', imports=["linkml:meta"])
    sv = SchemaView(schema)
    all_classes = sv.all_classes()
    assert len(all_classes) > 20
    schema_str = yaml_dumper.dumps(schema)
    sv = SchemaView(schema_str)
    assert len(sv.all_classes()) > 20
    assert sorted(all_classes) == sorted(sv.all_classes())


def test_non_linkml_remote_import():
    """
    Test that a remote import _not_ using the linkml prefix works

    See: https://github.com/linkml/linkml/issues/1627
    """
    schema = SchemaDefinition(
        id='test_non_linkml_remote_import',
        name='test_non_linkml_remote_import',
        prefixes=[
            Prefix(
                prefix_prefix="foo",
                prefix_reference="https://w3id.org/linkml/"
            )
        ],
        imports=["foo:types"],
        slots=[SlotDefinition(name="an_int", range="integer")],
        classes=[ClassDefinition(name="AClass", slots=["an_int"])]
    )
    sv = SchemaView(schema)
    slots = sv.class_induced_slots("AClass", imports=True)
    assert len(slots) == 1


def test_traversal():
    schema = SchemaDefinition(id='test', name='traversal-test')
    view = SchemaView(schema)
    view.add_class(ClassDefinition('Root', mixins=['RootMixin']))
    view.add_class(ClassDefinition('A', is_a='Root', mixins=['Am1', 'Am2', 'AZ']))
    view.add_class(ClassDefinition('B', is_a='A', mixins=['Bm1', 'Bm2', 'BY']))
    view.add_class(ClassDefinition('C', is_a='B', mixins=['Cm1', 'Cm2', 'CX']))
    view.add_class(ClassDefinition('RootMixin', mixin=True))
    view.add_class(ClassDefinition('Am1', is_a='RootMixin', mixin=True))
    view.add_class(ClassDefinition('Am2', is_a='RootMixin', mixin=True))
    view.add_class(ClassDefinition('Bm1', is_a='Am1', mixin=True))
    view.add_class(ClassDefinition('Bm2', is_a='Am2', mixin=True))
    view.add_class(ClassDefinition('Cm1', is_a='Bm1', mixin=True))
    view.add_class(ClassDefinition('Cm2', is_a='Bm2', mixin=True))
    view.add_class(ClassDefinition('AZ', is_a='RootMixin', mixin=True))
    view.add_class(ClassDefinition('BY', is_a='RootMixin', mixin=True))
    view.add_class(ClassDefinition('CX', is_a='RootMixin', mixin=True))

    def check(ancs: list, expected: list):
        assert ancs == expected

    check(view.class_ancestors('C', depth_first=True),
          ['C', 'Cm1', 'Cm2', 'CX', 'B', 'Bm1', 'Bm2', 'BY', 'A', 'Am1', 'Am2', 'AZ', 'Root', 'RootMixin'])
    check(view.class_ancestors('C', depth_first=False),
          ['C', 'Cm1', 'Cm2', 'CX', 'B', 'Bm1', 'Bm2', 'RootMixin', 'BY', 'A', 'Am1', 'Am2', 'AZ', 'Root'])
    check(view.class_ancestors('C', mixins=False),
          ['C', 'B', 'A', 'Root'])
    check(view.class_ancestors('C', is_a=False),
          ['C', 'Cm1', 'Cm2', 'CX'])


def test_slot_inheritance():
    schema = SchemaDefinition(id='test', name='test')
    view = SchemaView(schema)
    view.add_class(ClassDefinition('C', slots=['s1', 's2']))
    view.add_class(ClassDefinition('D'))
    view.add_class(ClassDefinition('Z'))
    view.add_class(ClassDefinition('W'))
    # view.add_class(ClassDefinition('C2',
    #                               is_a='C')
    #                              # slot_usage=[SlotDefinition(s1, range='C2')])
    view.add_slot(SlotDefinition('s1', multivalued=True, range='D'))
    view.add_slot(SlotDefinition('s2', is_a='s1'))
    view.add_slot(SlotDefinition('s3', is_a='s2', mixins=['m1']))
    view.add_slot(SlotDefinition('s4', is_a='s2', mixins=['m1'], range='W'))
    view.add_slot(SlotDefinition('m1', mixin=True, multivalued=False, range='Z'))
    slot1 = view.induced_slot('s1', 'C')
    assert slot1.is_a is None
    assert slot1.range == 'D'
    assert slot1.multivalued is not None
    slot2 = view.induced_slot('s2', 'C')
    assert slot2.is_a == 's1'
    assert slot2.range == 'D'
    assert slot2.multivalued is not None
    slot3 = view.induced_slot('s3', 'C')
    assert slot3.multivalued is not None
    assert slot3.range == 'Z'
    slot4 = view.induced_slot('s4', 'C')
    assert slot4.multivalued is not None
    assert slot4.range == 'W'
    # test dangling
    view.add_slot(SlotDefinition('s5', is_a='does-not-exist'))
    with pytest.raises(ValueError):
        view.slot_ancestors('s5')


def test_attribute_inheritance():
    """
    Tests attribute inheritance edge cases
    :return:
    """
    view = SchemaView(os.path.join(INPUT_DIR, 'attribute_edge_cases.yaml'))
    expected = [
        ('Root', 'a1', None, "a1"),
        ('Root', 'a2', None, "a2"),
        ('Root', 'a3', None, "a3"),
        ('C1', 'a1', True, "a1m1"),
        ('C1', 'a2', True, "a2c1"),
        ('C1', 'a3', None, "a3"),
        ('C1', 'a4', None, "a4"),
        ('C2', 'a1', False, "a1m2"),
        ('C2', 'a2', True, "a2c2"),
        ('C2', 'a3', None, "a3"),
        ('C2', 'a4', True, "a4m2"),
        ('C1x', 'a1', True, "a1m1"),
        ('C1x', 'a2', True, "a2c1x"),
        ('C1x', 'a3', None, "a3"),
        ('C1x', 'a4', None, "a4"),
    ]
    for cn, sn, req, desc in expected:
        slot = view.induced_slot(sn, cn)
        assert req == slot.required, f"in: {cn}.{sn}"
        assert desc == slot.description, f"in: {cn}.{sn}"
        assert 'string' == slot.range, f"in: {cn}.{sn}"


def test_ambiguous_attributes():
    """
    Tests behavior where multiple attributes share the same name
    """
    schema = SchemaDefinition(id='test', name='test')
    view = SchemaView(schema)
    a1 = SlotDefinition('a1', range='string')
    a2 = SlotDefinition('a2', range='FooEnum')
    a3 = SlotDefinition('a3', range='C3')
    view.add_class(ClassDefinition('C1', attributes={a1.name: a1, a2.name: a2, a3.name: a3}))
    a1x = SlotDefinition('a1', range='integer')
    a2x = SlotDefinition('a2', range='BarEnum')
    view.add_class(ClassDefinition('C2', attributes={a1x.name: a1x, a2x.name: a2x}))
    # a1 and a2 are ambiguous: only stub information available
    # without class context
    assert view.get_slot(a1.name).range is None
    assert view.get_slot(a2.name).range is None
    assert view.get_slot(a3.name).range is not None
    assert len(view.all_slots(attributes=True)) == 3
    assert len(view.all_slots(attributes=False)) == 0
    # default is to include attributes
    assert len(view.all_slots()) == 3
    assert view.induced_slot(a3.name).range == a3.range
    assert view.induced_slot(a1.name, 'C1').range == a1.range
    assert view.induced_slot(a2.name, 'C1').range == a2.range
    assert view.induced_slot(a1x.name, 'C2').range == a1x.range
    assert view.induced_slot(a2x.name, 'C2').range == a2x.range


def test_metamodel_in_schemaview():
    view = package_schemaview('linkml_runtime.linkml_model.meta')
    assert 'meta' in view.imports_closure()
    assert 'linkml:types' in view.imports_closure()
    assert 'meta' in view.imports_closure(imports=False)
    assert 'linkml:types' not in view.imports_closure(imports=False)
    assert len(view.imports_closure(imports=False)) == 1
    all_classes = list(view.all_classes().keys())
    all_classes_no_imports = list(view.all_classes(imports=False).keys())
    for cn in ['class_definition', 'type_definition', 'slot_definition']:
        assert cn in all_classes
        assert cn in all_classes_no_imports
        assert view.get_identifier_slot(cn).name == 'name'
    for cn in ['annotation', 'extension']:
        assert cn in all_classes, "imports should be included by default"
        assert cn not in all_classes_no_imports, "imported class unexpectedly included"
    for sn in ['id', 'name', 'description']:
        assert sn in view.all_slots()
    for tn in ['uriorcurie', 'string', 'float']:
        assert tn in view.all_types()
    for tn in ['uriorcurie', 'string', 'float']:
        assert tn not in view.all_types(imports=False)
    for cn, c in view.all_classes().items():
        uri = view.get_uri(cn, expand=True)
        assert uri is not None
        if cn != 'structured_alias' and cn != 'UnitOfMeasure' and cn != 'ValidationReport' and \
                cn != 'ValidationResult':
            assert 'https://w3id.org/linkml/' in uri
        induced_slots = view.class_induced_slots(cn)
        for s in induced_slots:
            exp_slot_uri = view.get_uri(s, expand=True)
            assert exp_slot_uri is not None


def test_get_classes_by_slot():
    sv = SchemaView(SCHEMA_WITH_IMPORTS)

    slot = sv.get_slot(AGE_IN_YEARS)

    actual_result = sv.get_classes_by_slot(slot)
    expected_result = ["Person"]

    assert sorted(expected_result) == sorted(actual_result)

    actual_result = sv.get_classes_by_slot(slot, include_induced=True)
    expected_result = ["Person", "Adult"]

    assert sorted(actual_result) == sorted(expected_result)


def test_materialize_patterns():
    sv = SchemaView(SCHEMA_WITH_STRUCTURED_PATTERNS)

    sv.materialize_patterns()

    height_slot = sv.get_slot("height")
    weight_slot = sv.get_slot("weight")

    assert height_slot.pattern == "\d+[\.\d+] (centimeter|meter|inch)"
    assert weight_slot.pattern == "\d+[\.\d+] (kg|g|lbs|stone)"


def test_materialize_patterns_slot_usage():
    sv = SchemaView(SCHEMA_WITH_STRUCTURED_PATTERNS)

    sv.materialize_patterns()

    name_slot_usage = sv.get_class("FancyPersonInfo").slot_usage['name']

    assert name_slot_usage.pattern == "\\S+ \\S+-\\S+"


def test_materialize_patterns_attribute():
    sv = SchemaView(SCHEMA_WITH_STRUCTURED_PATTERNS)

    sv.materialize_patterns()

    weight_attribute = sv.get_class('ClassWithAttributes').attributes['weight']

    assert weight_attribute.pattern == "\d+[\.\d+] (kg|g|lbs|stone)"


def test_mergeimports():
    sv = SchemaView(SCHEMA_WITH_IMPORTS, merge_imports=False)
    # activity class is in core, but not in kitchen_sink
    classes_list = list(sv.schema.classes.keys())
    assert "activity" not in classes_list

    # was generated by slot is in core, but not in kitchen_sink
    slots_list = list(sv.schema.slots.keys())
    assert "was generated by" not in slots_list

    # list of prefixes only in kitchen_sink
    prefixes_list = list(sv.schema.prefixes.keys())
    assert sorted(["pav", "dce", "lego", "linkml", "biolink", "ks", "RO", "BFO", "tax"]) == sorted(prefixes_list)

    # merge_imports=True, so activity class should be present
    sv = SchemaView(SCHEMA_WITH_IMPORTS, merge_imports=True)
    classes_list = list(sv.schema.classes.keys())
    assert "activity" in classes_list

    slots_list = list(sv.schema.slots.keys())
    assert "was generated by" in slots_list

    prefixes_list = list(sv.schema.prefixes.keys())
    if 'schema' not in prefixes_list:
        prefixes_list.append('schema')
    assert sorted(["pav", "dce", "lego", "linkml", "biolink", "ks", "RO", "BFO", "tax", "core", "prov", "xsd", "schema", "shex"]) == sorted(prefixes_list)


def test_is_inlined():
    schema_path = os.path.join(INPUT_DIR, "schemaview_is_inlined.yaml")
    sv = SchemaView(schema_path)
    cases = [
        # slot name, expected is_inline
        ("a_thing_with_id", False),
        ("inlined_thing_with_id", True),
        ("inlined_as_list_thing_with_id", True),
        ("a_thing_without_id", True),
        ("inlined_thing_without_id", True),
        ("inlined_as_list_thing_without_id", True),
        ("an_integer", False),
        ("inlined_integer", False),
        ("inlined_as_list_integer", False)
    ]
    for slot_name, expected_result in cases:
        slot = sv.get_slot(slot_name)
        actual_result = sv.is_inlined(slot)
        assert actual_result == expected_result

