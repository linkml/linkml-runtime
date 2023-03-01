from logging import warning
from typing import Optional, Union, Dict, List

from rdflib import Namespace, URIRef
from curies import Converter, Record

class CurieNamespaceCatalog(object):
    catalog: Dict[str, "CurieNamespace"]
    def __init__(self) -> None:
        self.namespaces = []
        self._converter: Optional[Converter] = None

    @property
    def converter(self):
        if not self._converter:
            self._converter = self._buildConverter()
        return self._converter

    def _buildConverter(self):
        records = []
        namespaces_to_treat = self.namespaces[:]
        while len(namespaces_to_treat) > 0:
            ns = namespaces_to_treat.pop(0)
            prefix = ns.prefix
            uri = str(ns)
            all_prefixes = [prefix]
            all_uris = [uri]
            iteration_needed = True
            while iteration_needed:
                iteration_needed = False
                for possible_synonym in namespaces_to_treat[:]:
                    if possible_synonym.prefix in all_prefixes:
                        all_uris.append(str(possible_synonym))
                        namespaces_to_treat.remove(possible_synonym)
                        iteration_needed = True
                    if str(possible_synonym) in all_uris:
                        all_prefixes.append(possible_synonym.prefix)
                        namespaces_to_treat.remove(possible_synonym)
                        iteration_needed = True
            records.append(Record(prefix, uri , [x for x in all_prefixes if not x == prefix], [x for x in all_uris if not x == uri]))
        return Converter(records=records)




    def to_curie(self, uri: Union[str, URIRef]) -> str:
        return self.converter.compress(uri)

    def to_uri(self, curie: str) -> Optional[URIRef]:
        expanded = self.converter.expand(curie)
        return None if expanded is None else URIRef(expanded) 
    
    def add_namespace(self,ns: "CurieNamespace"):
        self.namespaces.append(ns)
        self._converter = None
    
    @classmethod
    def create(cls, *namespaces: List["CurieNamespace"]):
        cat = CurieNamespaceCatalog()
        [cat.add_namespace(x) for x in namespaces]
        return cat

    def clear(self):
        self.catalog = dict()
    
    def as_dict(self):
        return self.catalog.copy()


class CurieNamespace(Namespace):
    def __new__(cls, prefix: str, ns: Union[str, URIRef]):
        rt = Namespace.__new__(cls, str(ns) if not isinstance(ns, bytes) else ns)
        rt.prefix = prefix
        return rt

    def curie(self, reference: Optional[str] = '') -> str:
        return self.prefix + ':' + reference

    def addTo(self, catalog: CurieNamespaceCatalog) -> "CurieNamespace":
        catalog.add_namespace(self)
        return self
