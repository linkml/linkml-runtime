import logging

import pytest

from linkml_runtime.linkml_model.meta import (
    ClassDefinition,
    SlotDefinition,
)
from linkml_runtime.processing import inlining
from linkml_runtime.utils.schema_builder import SchemaBuilder


def prepare_schema(with_identifier, inlined, inlined_as_list):
    builder = SchemaBuilder()

    id = SlotDefinition(name="id", identifier=True)
    builder.add_slot(id)

    range_class = ClassDefinition(name="RangeClass")
    if with_identifier:
        range_class.slots = ["id"]
    builder.add_class(range_class)

    slot = SlotDefinition(name="slot_under_test", range=range_class.name)
    if isinstance(inlined, bool):
        slot.inlined = inlined
    if isinstance(inlined_as_list, bool):
        slot.inlined_as_list = inlined_as_list
    builder.add_slot(slot)

    slot_type = SlotDefinition(name="slot_with_type", range="int")
    if isinstance(inlined, bool):
        slot_type.inlined = inlined
    if isinstance(inlined_as_list, bool):
        slot_type.inlined_as_list = inlined_as_list
    builder.add_slot(slot_type)

    return (slot, slot_type, {"schema": builder.schema})


@pytest.mark.parametrize(
    ("with_identifier", "inlined", "inlined_as_list", "expected_inlined", "expected_inlined_as_list"),
    [
        (True, True, True, True, True),
        (True, True, False, True, False),
        (True, False, None, False, None),
        (False, True, True, True, True),
    ],
)
def test_report_ok(with_identifier, inlined, inlined_as_list, expected_inlined, expected_inlined_as_list, caplog):
    """Test that combinations that are clear an unproblematic only generate debug output."""
    logger = logging.getLogger("Test")
    caplog.set_level(logging.DEBUG)

    slot, _, schema_map = prepare_schema(with_identifier, inlined, inlined_as_list)
    fixed_inlined, fixed_inlined_as_list = inlining.process(slot, schema_map, logger)
    assert fixed_inlined == expected_inlined
    assert fixed_inlined_as_list == expected_inlined_as_list
    for logrecord in caplog.records:
        assert logrecord.levelname == "DEBUG"
        assert " complete inlining specification" in logrecord.message


@pytest.mark.parametrize(
    ("with_identifier", "inlined", "inlined_as_list", "expected_inlined_as_list"),
    [
        # overriding specified `inlined: false` with `inlined: true`!!
        (True, False, True, True),
    ],
)
def test_force_inlined(with_identifier, inlined, inlined_as_list, expected_inlined_as_list, caplog):
    """Test that combinations that end up forcing `inlined: true` does so and generate a warning."""
    logger = logging.getLogger("Test")
    caplog.set_level(logging.WARNING)

    slot, _, schema_map = prepare_schema(with_identifier, inlined, inlined_as_list)
    fixed_inlined, fixed_inlined_as_list = inlining.process(slot, schema_map, logger)
    assert fixed_inlined
    assert fixed_inlined_as_list == expected_inlined_as_list
    for logrecord in caplog.records:
        assert logrecord.levelname == "WARNING"
        assert "Forcing `inlined: true`!!" in logrecord.message


@pytest.mark.parametrize(
    ("with_identifier", "inlined", "inlined_as_list", "expected_inlined_as_list"),
    [
        # applying implicit default!!
        (True, None, True, True),
        # applying implicit default!!
        (False, None, True, True),
    ],
)
def test_default_inlined(with_identifier, inlined, inlined_as_list, expected_inlined_as_list, caplog):
    """Test that combinations that end up forcing `inlined: true` does so and generate a warning."""
    logger = logging.getLogger("Test")
    caplog.set_level(logging.INFO)

    slot, _, schema_map = prepare_schema(with_identifier, inlined, inlined_as_list)
    fixed_inlined, fixed_inlined_as_list = inlining.process(slot, schema_map, logger)
    assert fixed_inlined
    assert fixed_inlined_as_list == expected_inlined_as_list
    for logrecord in caplog.records:
        assert logrecord.levelname == "INFO"
        assert "Forcing `inlined: true`!!" in logrecord.message


@pytest.mark.parametrize(
    ("with_identifier", "inlined", "inlined_as_list", "expected_inlined", "expected_inlined_as_list"),
    [
        # what type of inlining to use?
        (True, True, None, True, None),
        # why specifying inlining type if no inlining?
        (True, False, False, False, False),
        # why specifying inlining type if inlining not requested?
        (True, None, False, None, False),
        # no defaults, in-code implicit defaults will apply
        (True, None, None, None, None),
        # how to select a key for an object without an identifier?
        (False, True, False, True, False),
        # no defaults, in-code implicit defaults will apply
        (False, True, None, True, None),
        # how to add a reference to an object without an identifier?
        (False, False, True, False, True),
        # how to add a reference to an object without an identifier?
        (False, False, False, False, False),
        # how to add a reference to an object without an identifier?
        (False, False, None, False, None),
        # why specifying inlining type if inlining not requested?
        (False, None, False, None, False),
        # no defaults, in-code implicit defaults will apply
        (False, None, None, None, None),
    ],
)
def test_info_inconsistencies(
    with_identifier, inlined, inlined_as_list, expected_inlined, expected_inlined_as_list, caplog
):
    """Test that combinations that are somehow illogical or incomplete are reported."""
    logger = logging.getLogger("Test")
    caplog.set_level(logging.INFO)

    slot, _, schema_map = prepare_schema(with_identifier, inlined, inlined_as_list)
    fixed_inlined, fixed_inlined_as_list = inlining.process(slot, schema_map, logger)
    assert fixed_inlined == expected_inlined
    assert fixed_inlined_as_list == expected_inlined_as_list
    for logrecord in caplog.records:
        assert logrecord.levelname == "INFO"
        assert "illogic or incomplete inlining specification" in logrecord.message


@pytest.mark.parametrize(
    ("with_identifier", "inlined", "inlined_as_list"),
    [
        (True, True, True),
        (True, True, False),
        (True, True, None),
        (True, False, True),
        (True, False, False),
        (True, False, None),
        (True, None, True),
        (True, None, False),
        (True, None, None),
        (False, True, True),
        (False, True, False),
        (False, True, None),
        (False, False, True),
        (False, False, False),
        (False, False, None),
        (False, None, True),
        (False, None, False),
        (False, None, None),
    ],
)
def test_slot_type(with_identifier, inlined, inlined_as_list):
    """Test that slots with a type as range returns (None, None)."""
    logger = logging.getLogger("Test")
    _, slot, schema_map = prepare_schema(with_identifier, inlined, inlined_as_list)
    fixed_inlined, fixed_inlined_as_list = inlining.process(slot, schema_map, logger)
    assert fixed_inlined is None
    assert fixed_inlined_as_list is None
