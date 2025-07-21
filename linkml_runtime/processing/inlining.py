from copy import deepcopy
from logging import Logger
from typing import cast

from linkml_runtime.linkml_model.meta import (
    ClassDefinitionName,
    SchemaDefinition,
    SlotDefinition,
)


def _create_function_dispatcher(slot: SlotDefinition, logger: Logger) -> None:
    """Function dispatcher for slot inlining processing"""

    def set_inlined_and_warn(range_class_has_identifier: bool) -> None:
        slot.inlined = True
        text_identifier = "with an identifier" if range_class_has_identifier else "without an identifier"
        msg = (
            f"Slot '{slot.name}' is requesting for an object {text_identifier} inlining as a "
            + "list, but no inlining requested! Forcing `inlined: true`!!"
        )
        logger.warning(msg)

    def set_inlined_and_report(range_class_has_identifier: bool) -> None:
        slot.inlined = True
        text_identifier = "with an identifier" if range_class_has_identifier else "without an identifier"
        msg = (
            f"Slot '{slot.name}' is requesting for an object {text_identifier} inlining as a "
            + "list, but no inlining requested! Forcing `inlined: true`!!"
        )
        logger.info(msg)

    def debug_output(range_class_has_identifier: bool) -> None:
        msg = (
            f"Slot '{slot.name}' has a complete inlining specification: "
            + f"range class has identifier: {range_class_has_identifier},"
        )
        if slot.inlined_as_list is None:
            msg += f"`inlined: {slot.inlined}`, `inlined_as_list` unspecified."
        else:
            msg += f"`inlined: {slot.inlined}` and `inlined_as_list: {slot.inlined_as_list}`"
        logger.debug(msg)

    def info(range_class_has_identifier: bool) -> None:
        text_identifier = "with an identifier" if range_class_has_identifier else "without an identifier"
        msg = (
            f"Slot '{slot.name}' has following illogic or incomplete inlining "
            + f"specification: `inlined: {slot.inlined}` and `inlined_as_list: "
            + f"{slot.inlined_as_list}` for objects {text_identifier}"
        )
        logger.info(msg)

    function_map = {
        # OK
        (True, True, True): debug_output,
        # OK
        (True, True, False): debug_output,
        # what type of inlining to use?
        (True, True, None): info,
        # overriding specified value!!
        (True, False, True): set_inlined_and_warn,
        # why specifying inlining type if no inlining?
        (True, False, False): info,
        # OK
        (True, False, None): debug_output,
        # applying implicit default!!
        (True, None, True): set_inlined_and_report,
        # why specifying inlining type if inlining not requested?
        (True, None, False): info,
        # no defaults, in-code implicit defaults will apply
        (True, None, None): info,
        # OK
        (False, True, True): debug_output,
        # how to select a key for an object without an identifier?
        (False, True, False): info,
        # no defaults, in-code implicit defaults will apply
        (False, True, None): info,
        # how to add a reference to an object without an identifier?
        (False, False, True): info,
        # how to add a reference to an object without an identifier?
        (False, False, False): info,
        # how to add a reference to an object without an identifier?
        (False, False, None): info,
        # applying implicit default!!
        (False, None, True): set_inlined_and_report,
        # why specifying inlining type if inlining not requested?
        (False, None, False): info,
        # no defaults, in-code implicit defaults will apply
        (False, None, None): info,
    }

    def dispatch(range_class_has_identifier, inlined, inlined_as_list):
        # func = function_map.get((range_class_has_identifier, inlined, inlined_as_list), default_function)
        func = function_map.get((range_class_has_identifier, inlined, inlined_as_list))
        return func(range_class_has_identifier)

    return dispatch


def process(slot: SlotDefinition, schema_map: dict[str, SchemaDefinition], logger: Logger) -> (bool, bool):
    """
    Processing the inlining behavior of a slot, including the type of inlining
    (as a list or as a dictionary).

    Processing encompasses analyzing the combination of elements relevant for
    object inlining (reporting the result of the analysis with different logging
    levels) and enforcing certain values.

    It is important to take into account following:
    - slot.inlined and slot.inlined_as_list can have three different values:
    True, False or None (if nothing specified in the schema)
    - if a class has an identifier is a pure boolean

    Changes to `inlined` are applied directly on the provided slot object.

    :param slot: the slot to process
    :param schema: the schema in which the slot is contained
    :param logger: the logger to use
    """

    fixed_slot = deepcopy(slot)
    # first of all, validate that the values of `inlined` and `inlined_as_list` are legal
    # either `True` or `False` (if specified) or `None` (if nothing specified)
    for value in ("inlined", "inlined_as_list"):
        if getattr(fixed_slot, value) not in (True, False, None):
            raise ValueError(
                f"Invalid value for '{value}' in the schema for slot "
                + f"'{fixed_slot.name}': '{getattr(fixed_slot, value)}'"
            )
    range_class = None
    for schema in schema_map.values():
        if cast(ClassDefinitionName, fixed_slot.range) in schema.classes:
            range_class = schema.classes[cast(ClassDefinitionName, fixed_slot.range)]
            break
    # range is a type
    if range_class is None:
        return (None, None)
    range_has_identifier = False
    for sn in range_class.slots:
        for schema in schema_map.values():
            if sn in schema.slots:
                range_has_identifier = bool(schema.slots[sn].identifier or schema.slots[sn].key)
                break
        else:
            continue
        break

    dispatcher = _create_function_dispatcher(fixed_slot, logger)
    dispatcher(range_has_identifier, fixed_slot.inlined, fixed_slot.inlined_as_list)

    return (fixed_slot.inlined, fixed_slot.inlined_as_list)


def is_inlined(slot: SlotDefinition, schema_map: dict[str, SchemaDefinition], logger: Logger) -> (bool, bool):
    return bool(process(slot, schema_map, logger)[0])


def is_inlined_as_list(slot: SlotDefinition, schema_map: dict[str, SchemaDefinition], logger: Logger) -> (bool, bool):
    return bool(process(slot, schema_map, logger)[1])
