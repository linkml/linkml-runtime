import sys
import warnings

# This patch is a temporary implementation of a proposed fix for https://github.com/python/cpython/issues/92052
# It replaces the `dataclass` and `_process_cls` methods in the default library.  The only significant changes are
# on lines 133 (more or less) and 142 - see the issue for the exact lines.
#
# Once the issue has been fixed we can tighten up the test below to select only the versions where it hasn't been,
# and then (perhaps) add a deprecated message to encourage folks to stop importing the patch period.
from typing import Callable, Any

if sys.version_info < (3, 10):
    warnings.warn(f"dataclass patch is not available for any version other than 3.10.0")
    from dataclasses import dataclass

    DC_PATCH_INSTALLED = False
else:
    import dataclasses

    # The set of classes and ancestors that have been directly declared as dataclasses (vs. inherited)
    _DECLARED_DATA_CLASSES = '__declared_dataclasses__'


    def dataclass(cls=None, /, *, init=True, repr=True, eq=True, order=False,
                  unsafe_hash=False, frozen=False, match_args=True,
                  kw_only=False, slots=False, weakref_slot=False):
        """Returns the same class as was passed in, with dunder methods
        added based on the fields defined in the class.

        Examines PEP 526 __annotations__ to determine fields.

        If init is true, an __init__() method is added to the class. If
        repr is true, a __repr__() method is added. If order is true, rich
        comparison dunder methods are added. If unsafe_hash is true, a
        __hash__() method function is added. If frozen is true, fields may
        not be assigned to after instance creation. If match_args is true,
        the __match_args__ tuple is added. If kw_only is true, then by
        default all fields are keyword-only. If slots is true, an
        __slots__ attribute is added.
        """

        def wrap(cls):
            seen = getattr(cls, _DECLARED_DATA_CLASSES, None)
            if seen is None:
                seen = set()
                setattr(cls, _DECLARED_DATA_CLASSES, seen)
            elif id(cls) in seen:
                return cls
            seen.add(id(cls))
            return dataclasses._process_class(cls, init, repr, eq, order, unsafe_hash,
                                  frozen, match_args, kw_only, slots)

        # See if we're being called as @dataclass or @dataclass().
        if cls is None:
            # We're called with parens.
            return wrap

        # We're called as @dataclass without parens.
        return wrap(cls)


    def is_direct_dataclass(cls: type):
        """ Returns True if cls is declared as a dataclass (vs. inherits from) """
        return id(cls) in getattr(cls, _DECLARED_DATA_CLASSES, set())

    dataclasses.dataclass = dataclass
    DC_PATCH_INSTALLED = True
print(f"Dataclass patch is {'installed' if DC_PATCH_INSTALLED else 'not installed'}")

