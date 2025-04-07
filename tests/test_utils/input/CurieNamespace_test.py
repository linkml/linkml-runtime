# Auto generated from None by pythongen.py version: 0.9.0
# Generation date: 2023-01-31T13:57:38
# Schema: inline-dict-test
#
# id: http://example.org
# description: test
# license: https://creativecommons.org/publicdomain/zero/1.0/

import dataclasses
import sys
import re
from pprint import pprint

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
from rdflib import Namespace, URIRef, DC
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.utils.metamodelcore import Bool, Decimal, ElementIdentifier, NCName, NodeIdentifier, URI, URIorCURIE, XSDDate, XSDDateTime, XSDTime

metamodel_version = "1.7.0"
version = None

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
SHEX = CurieNamespace('shex', 'http://www.w3.org/ns/shex#')
XSD = CurieNamespace('xsd', 'http://www.w3.org/2001/XMLSchema#')
DEFAULT_ = CurieNamespace('', 'http://example.org/')


# Types
class String(str):
    """ A character string """
    type_class_uri = XSD.string
    type_class_curie = "xsd:string"
    type_name = "string"
    type_model_uri = URIRef("http://example.org/String")


class Integer(int):
    """ An integer """
    type_class_uri = XSD.integer
    type_class_curie = "xsd:integer"
    type_name = "integer"
    type_model_uri = URIRef("http://example.org/Integer")


class Boolean(Bool):
    """ A binary (true or false) value """
    type_class_uri = XSD.boolean
    type_class_curie = "xsd:boolean"
    type_name = "boolean"
    type_model_uri = URIRef("http://example.org/Boolean")


class Float(float):
    """ A real number that conforms to the xsd:float specification """
    type_class_uri = XSD.float
    type_class_curie = "xsd:float"
    type_name = "float"
    type_model_uri = URIRef("http://example.org/Float")


class Double(float):
    """ A real number that conforms to the xsd:double specification """
    type_class_uri = XSD.double
    type_class_curie = "xsd:double"
    type_name = "double"
    type_model_uri = URIRef("http://example.org/Double")


class Decimal(Decimal):
    """ A real number with arbitrary precision that conforms to the xsd:decimal specification """
    type_class_uri = XSD.decimal
    type_class_curie = "xsd:decimal"
    type_name = "decimal"
    type_model_uri = URIRef("http://example.org/Decimal")


class Time(XSDTime):
    """ A time object represents a (local) time of day, independent of any particular day """
    type_class_uri = XSD.dateTime
    type_class_curie = "xsd:dateTime"
    type_name = "time"
    type_model_uri = URIRef("http://example.org/Time")


class Date(XSDDate):
    """ a date (year, month and day) in an idealized calendar """
    type_class_uri = XSD.date
    type_class_curie = "xsd:date"
    type_name = "date"
    type_model_uri = URIRef("http://example.org/Date")


class Datetime(XSDDateTime):
    """ The combination of a date and time """
    type_class_uri = XSD.dateTime
    type_class_curie = "xsd:dateTime"
    type_name = "datetime"
    type_model_uri = URIRef("http://example.org/Datetime")


class DateOrDatetime(str):
    """ Either a date or a datetime """
    type_class_uri = LINKML.DateOrDatetime
    type_class_curie = "linkml:DateOrDatetime"
    type_name = "date_or_datetime"
    type_model_uri = URIRef("http://example.org/DateOrDatetime")


class Uriorcurie(URIorCURIE):
    """ a URI or a CURIE """
    type_class_uri = XSD.anyURI
    type_class_curie = "xsd:anyURI"
    type_name = "uriorcurie"
    type_model_uri = URIRef("http://example.org/Uriorcurie")


class Uri(URI):
    """ a complete URI """
    type_class_uri = XSD.anyURI
    type_class_curie = "xsd:anyURI"
    type_name = "uri"
    type_model_uri = URIRef("http://example.org/Uri")


class Ncname(NCName):
    """ Prefix part of CURIE """
    type_class_uri = XSD.string
    type_class_curie = "xsd:string"
    type_name = "ncname"
    type_model_uri = URIRef("http://example.org/Ncname")


class Objectidentifier(ElementIdentifier):
    """ A URI or CURIE that represents an object in the model. """
    type_class_uri = SHEX.iri
    type_class_curie = "shex:iri"
    type_name = "objectidentifier"
    type_model_uri = URIRef("http://example.org/Objectidentifier")


class Nodeidentifier(NodeIdentifier):
    """ A URI, CURIE or BNODE that represents a node in a model. """
    type_class_uri = SHEX.nonLiteral
    type_class_curie = "shex:nonLiteral"
    type_name = "nodeidentifier"
    type_model_uri = URIRef("http://example.org/Nodeidentifier")


# Class references
class NamedThingId(extended_str):
    pass


class PersonId(NamedThingId):
    pass


class OrganisationId(NamedThingId):
    pass


class NonProfitId(OrganisationId):
    pass


class ForProfitId(OrganisationId):
    pass


@dataclass
class NamedThing(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("http://example.org/NamedThing")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "NamedThing"
    class_model_curie: ClassVar[str] = "None"
    class_model_uri: ClassVar[URIRef] = URIRef("http://example.org/NamedThing")

    id: Union[str, NamedThingId] = None
    full_name: Optional[str] = None
    thingtype: URIorCURIE = dataclasses.field(init=False)

    @property
    def thingtype(self) -> URIorCURIE:
        return URIorCURIE(self.class_class_uri)

    @thingtype.setter
    def thingtype(self, v: Any) -> None:
        pass

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, NamedThingId):
            self.id = NamedThingId(self.id)

        if self.full_name is not None and not isinstance(self.full_name, str):
            self.full_name = str(self.full_name)

        super().__post_init__(**kwargs)



    def __new__(cls, *args, **kwargs):
        uri = kwargs.pop("thingtype", cls.class_class_uri)
        target_cls = YAMLRoot._class_for_uri(uri)
        if target_cls is None:
            # Should this be a warning instead?  If so, what do we do with the new URI?
            raise ValueError(
                f"Wrong type designator value: class NamedThing has no subclass with class_class_uri='{uri}'")
        return super().__new__(target_cls, *args, **kwargs)



@dataclass
class Person(NamedThing):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("http://testbreaker/not-the-uri-you-expect")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "Person"
    class_model_curie: ClassVar[str] = "None"
    class_model_uri: ClassVar[URIRef] = URIRef("http://example.org/Person")

    id: Union[str, PersonId] = None
    height: Optional[int] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, PersonId):
            self.id = PersonId(self.id)

        if self.height is not None and not isinstance(self.height, int):
            self.height = int(self.height)

        super().__post_init__(**kwargs)



@dataclass
class Organisation(NamedThing):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("http://example.org/Organisation")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "Organisation"
    class_model_curie: ClassVar[str] = "None"
    class_model_uri: ClassVar[URIRef] = URIRef("http://example.org/Organisation")

    id: Union[str, OrganisationId] = None
    number_of_employees: Optional[int] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, OrganisationId):
            self.id = OrganisationId(self.id)

        if self.number_of_employees is not None and not isinstance(self.number_of_employees, int):
            self.number_of_employees = int(self.number_of_employees)

        super().__post_init__(**kwargs)



@dataclass
class NonProfit(Organisation):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("http://example.org/NonProfit")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "NonProfit"
    class_model_curie: ClassVar[str] = "None"
    class_model_uri: ClassVar[URIRef] = URIRef("http://example.org/NonProfit")

    id: Union[str, NonProfitId] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, NonProfitId):
            self.id = NonProfitId(self.id)

        super().__post_init__(**kwargs)



@dataclass
class ForProfit(Organisation):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("http://example.org/ForProfit")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "ForProfit"
    class_model_curie: ClassVar[str] = "None"
    class_model_uri: ClassVar[URIRef] = URIRef("http://example.org/ForProfit")

    id: Union[str, ForProfitId] = None
    target_profit_margin: Optional[float] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, ForProfitId):
            self.id = ForProfitId(self.id)

        if self.target_profit_margin is not None and not isinstance(self.target_profit_margin, float):
            self.target_profit_margin = float(self.target_profit_margin)

        super().__post_init__(**kwargs)



@dataclass
class Container(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("http://example.org/Container")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "Container"
    class_model_curie: ClassVar[str] = "None"
    class_model_uri: ClassVar[URIRef] = URIRef("http://example.org/Container")

    things: Optional[Union[Dict[Union[str, NamedThingId], Union[dict, NamedThing]], List[Union[dict, NamedThing]]]] = empty_dict()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        self._normalize_inlined_as_list(slot_name="things", slot_type=NamedThing, key_name="id", keyed=True)

        super().__post_init__(**kwargs)



@dataclass
class ContainerWithOneSibling(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("http://example.org/ContainerWithOneSibling")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "ContainerWithOneSibling"
    class_model_curie: ClassVar[str] = "None"
    class_model_uri: ClassVar[URIRef] = URIRef("http://example.org/ContainerWithOneSibling")

    persons: Optional[Union[Dict[Union[str, PersonId], Union[dict, Person]], List[Union[dict, Person]]]] = empty_dict()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        self._normalize_inlined_as_list(slot_name="persons", slot_type=Person, key_name="id", keyed=True)

        super().__post_init__(**kwargs)



# Enumerations


# Slots
