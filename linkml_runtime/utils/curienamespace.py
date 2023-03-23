from logging import warning
from typing import Optional, Union, Dict, List

from rdflib import Namespace, URIRef
from curies import Converter, Record

class CurieNamespaceCatalog(object):
    """
    A CurieNamespaceCatalog is a catalog of CurieNamespace objects
    its main purpose is to convert between uri's and curies for the namespaces in the catalog
    """
    def __init__(self) -> None:
        self.namespaces = []
        self._converter: Optional[Converter] = None

    @property
    def converter(self):
        """
        return a curies.Converter that knows all namespaces. 
        When multiple namespaces have the same prefix, they are added as uri synonyms to the converter.
        When there are two prefixes leading to the same uri, they are added as prefix synonyms to the converter.
        """
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




    def to_curie(self, uri: Union[str, URIRef]) -> Optional[str]:
        """
        Compress a URI to a CURIE, if possible.

        :param uri:
            A string representing a valid uniform resource identifier (URI)
        :returns:
            A compact URI if this converter could find an appropriate URI prefix, otherwise None.
        
        """
        if isinstance(uri, URIRef):
            uri = str(uri)
        return self.converter.compress(uri)

    def to_uri(self, curie: str) -> Optional[URIRef]:
        """
        Expand a CURIE to a URI, if possible.

        :param curie:
            A string representing a compact URI
        :returns:
            A URIRef if this converter contains a URI prefix for the prefix in this CURIE, otherwise None
        """
        expanded = self.converter.expand(curie)
        return None if expanded is None else URIRef(expanded) 
    
    def add_namespace(self,ns: "CurieNamespace"):
        """
        Adds a new namespace to the catalog.
        """
        self.namespaces.append(ns)
        self._converter = None
    
    @classmethod
    def create(cls, *namespaces: List["CurieNamespace"]):
        """
        creates a new catalog from the given namespaces
        """
        cat = CurieNamespaceCatalog()
        [cat.add_namespace(x) for x in namespaces]
        return cat



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
