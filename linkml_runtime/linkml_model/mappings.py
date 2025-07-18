# Auto generated from mappings.yaml by pythongen.py version: 0.0.1
# Generation date: 2024-06-27T23:15:23
# Schema: mappings
#
# id: https://w3id.org/linkml/mappings
# description: LinkML model for mappings
# license: https://creativecommons.org/publicdomain/zero/1.0/

from typing import Optional, Union

from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.utils.metamodelcore import URIorCURIE
from linkml_runtime.utils.slot import Slot

metamodel_version = "1.7.0"
version = "2.0.0"

# Namespaces
IAO = CurieNamespace("IAO", "http://purl.obolibrary.org/obo/IAO_")
OIO = CurieNamespace("OIO", "http://www.geneontology.org/formats/oboInOwl#")
LINKML = CurieNamespace("linkml", "https://w3id.org/linkml/")
RDF = CurieNamespace("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS = CurieNamespace("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
SKOS = CurieNamespace("skos", "http://www.w3.org/2004/02/skos/core#")
XSD = CurieNamespace("xsd", "http://www.w3.org/2001/XMLSchema#")
DEFAULT_ = LINKML


# Types

# Class references


# Enumerations


# Slots
class slots:
    pass


slots.mappings = Slot(
    uri=SKOS.mappingRelation,
    name="mappings",
    curie=SKOS.curie("mappingRelation"),
    model_uri=LINKML.mappings,
    domain=None,
    range=Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]],
)

slots.exact_mappings = Slot(
    uri=SKOS.exactMatch,
    name="exact mappings",
    curie=SKOS.curie("exactMatch"),
    model_uri=LINKML.exact_mappings,
    domain=None,
    range=Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]],
)

slots.close_mappings = Slot(
    uri=SKOS.closeMatch,
    name="close mappings",
    curie=SKOS.curie("closeMatch"),
    model_uri=LINKML.close_mappings,
    domain=None,
    range=Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]],
)

slots.related_mappings = Slot(
    uri=SKOS.relatedMatch,
    name="related mappings",
    curie=SKOS.curie("relatedMatch"),
    model_uri=LINKML.related_mappings,
    domain=None,
    range=Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]],
)

slots.narrow_mappings = Slot(
    uri=SKOS.narrowMatch,
    name="narrow mappings",
    curie=SKOS.curie("narrowMatch"),
    model_uri=LINKML.narrow_mappings,
    domain=None,
    range=Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]],
)

slots.broad_mappings = Slot(
    uri=SKOS.broadMatch,
    name="broad mappings",
    curie=SKOS.curie("broadMatch"),
    model_uri=LINKML.broad_mappings,
    domain=None,
    range=Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]],
)

slots.deprecated_element_has_exact_replacement = Slot(
    uri=LINKML.deprecated_element_has_exact_replacement,
    name="deprecated element has exact replacement",
    curie=LINKML.curie("deprecated_element_has_exact_replacement"),
    model_uri=LINKML.deprecated_element_has_exact_replacement,
    domain=None,
    range=Optional[Union[str, URIorCURIE]],
    mappings=[IAO["0100001"]],
)

slots.deprecated_element_has_possible_replacement = Slot(
    uri=LINKML.deprecated_element_has_possible_replacement,
    name="deprecated element has possible replacement",
    curie=LINKML.curie("deprecated_element_has_possible_replacement"),
    model_uri=LINKML.deprecated_element_has_possible_replacement,
    domain=None,
    range=Optional[Union[str, URIorCURIE]],
    mappings=[OIO["consider"]],
)
