# Auto generated from linkml_issue_497.yaml by pythongen.py version: 0.9.0
# Generation date: 2021-12-03T15:03:07
# Schema: test-inherited-ranges
#
# id: https://example.com/test-inherited-ranges
# description: a simple schema for testing if the range for base class propogates to the inherited class
# license: https://creativecommons.org/publicdomain/zero/1.0/

import dataclasses
import sys
import re
from jsonasobj2 import JsonObj, as_dict
from typing import Optional, List, Union, Dict, ClassVar, Any
from dataclasses import dataclass
from linkml_runtime.linkml_model.meta import EnumDefinition, PermissibleValue, PvFormulaOptions

from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.metamodelcore import empty_list, empty_dict, bnode
from linkml_runtime.utils.yamlutils import YAMLRoot, extended_str, extended_float, extended_int
from linkml_runtime.utils.dataclass_extensions_376 import dataclasses_init_fn_with_kwargs
from linkml_runtime.utils.formatutils import camelcase, underscore, sfx
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from rdflib import Namespace, URIRef
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.linkml_model.types import String

metamodel_version = "1.7.0"

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
DCTERMS = CurieNamespace('dcterms', 'http://purl.org/dc/terms/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
DEFAULT_ = CurieNamespace('', 'https://example.com/test-inherited-ranges/')


# Types

# Class references



class NamedThing(YAMLRoot):
    """
    a databased entity or concept/class
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("https://example.com/test-inherited-ranges/NamedThing")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "named thing"
    class_model_uri: ClassVar[URIRef] = URIRef("https://example.com/test-inherited-ranges/NamedThing")


@dataclass
class BiosampleProcessing(NamedThing):
    """
    A process that takes one or more biosamples as inputs and generates one or as outputs. Examples of outputs include
    samples cultivated from another sample or data objects created by instruments runs.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("https://example.com/test-inherited-ranges/BiosampleProcessing")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "biosample processing"
    class_model_uri: ClassVar[URIRef] = URIRef("https://example.com/test-inherited-ranges/BiosampleProcessing")

    has_input: Optional[Union[Union[dict, "Biosample"], List[Union[dict, "Biosample"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if not isinstance(self.has_input, list):
            self.has_input = [self.has_input] if self.has_input is not None else []
        self.has_input = [v if isinstance(v, Biosample) else Biosample(**as_dict(v)) for v in self.has_input]

        super().__post_init__(**kwargs)


@dataclass
class OmicsProcessing(BiosampleProcessing):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("https://example.com/test-inherited-ranges/OmicsProcessing")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "omics processing"
    class_model_uri: ClassVar[URIRef] = URIRef("https://example.com/test-inherited-ranges/OmicsProcessing")

    has_input: Optional[Union[Union[dict, NamedThing], List[Union[dict, NamedThing]]]] = empty_list()
    has_output: Optional[Union[Union[dict, NamedThing], List[Union[dict, NamedThing]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if not isinstance(self.has_input, list):
            self.has_input = [self.has_input] if self.has_input is not None else []
        self.has_input = [v if isinstance(v, NamedThing) else NamedThing(**as_dict(v)) for v in self.has_input]

        if not isinstance(self.has_output, list):
            self.has_output = [self.has_output] if self.has_output is not None else []
        self.has_output = [v if isinstance(v, NamedThing) else NamedThing(**as_dict(v)) for v in self.has_output]

        super().__post_init__(**kwargs)


class Biosample(NamedThing):
    """
    A material sample. It may be environmental (encompassing many organisms) or isolate or tissue. An environmental
    sample containing genetic material from multiple individuals is commonly referred to as a biosample.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("https://example.com/test-inherited-ranges/Biosample")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "biosample"
    class_model_uri: ClassVar[URIRef] = URIRef("https://example.com/test-inherited-ranges/Biosample")


# Enumerations


# Slots
class slots:
    pass

slots.id = Slot(uri=DEFAULT_.id, name="id", curie=DEFAULT_.curie('id'),
                   model_uri=DEFAULT_.id, domain=None, range=URIRef)

slots.name = Slot(uri=DEFAULT_.name, name="name", curie=DEFAULT_.curie('name'),
                   model_uri=DEFAULT_.name, domain=None, range=Optional[str])

slots.description = Slot(uri=DEFAULT_.description, name="description", curie=DEFAULT_.curie('description'),
                   model_uri=DEFAULT_.description, domain=None, range=Optional[str])

slots.has_input = Slot(uri=DEFAULT_.has_input, name="has input", curie=DEFAULT_.curie('has_input'),
                   model_uri=DEFAULT_.has_input, domain=NamedThing, range=Optional[Union[Union[dict, "NamedThing"], List[Union[dict, "NamedThing"]]]])

slots.has_output = Slot(uri=DEFAULT_.has_output, name="has output", curie=DEFAULT_.curie('has_output'),
                   model_uri=DEFAULT_.has_output, domain=NamedThing, range=Optional[Union[Union[dict, "NamedThing"], List[Union[dict, "NamedThing"]]]])

slots.biosample_processing_has_input = Slot(uri=DEFAULT_.has_input, name="biosample processing_has input", curie=DEFAULT_.curie('has_input'),
                   model_uri=DEFAULT_.biosample_processing_has_input, domain=BiosampleProcessing, range=Optional[Union[Union[dict, "Biosample"], List[Union[dict, "Biosample"]]]])
