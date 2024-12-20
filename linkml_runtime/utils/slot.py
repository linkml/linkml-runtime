from dataclasses import dataclass
from rdflib import URIRef
from re import Pattern, Match
from typing import Type, List, Optional, Any

@dataclass
class Slot:
    """ Runtime slot definition """
    uri: URIRef
    name: str
    curie: Optional[str]
    model_uri: URIRef

    domain: Optional[Type]
    range: Any
    mappings: Optional[List[URIRef]] = None
    pattern: Optional[re] = None
