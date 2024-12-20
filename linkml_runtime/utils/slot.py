from dataclasses import dataclass
from rdflib import URIRef
from typing import Type, List, Optional, Any
try:
    # Python 3.8, 3.9, 3.10
    from typing import re
except:
    # Python 3.11+
    import re

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
