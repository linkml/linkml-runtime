from logging import warning
from typing import Optional, Union, Dict

from rdflib import Namespace, URIRef


class CurieNamespace(Namespace):
    # We would prefer to use curies.Converter here, but there doesn't appear to be any way to build it incrementally
    catalog: Dict[str, "CurieNamespace"] = dict()

    @classmethod
    def to_curie(cls, uri: Union[str, URIRef]) -> str:
        uri = str(uri)
        candidate_ns = ""
        for prefix, ns in cls.catalog.items():
            if uri.startswith(ns) and len(ns) > len(candidate_ns):
                candidate_ns = ns
        if candidate_ns:
            return candidate_ns.curie(uri[len(candidate_ns):])
        return None

    @classmethod
    def to_uri(cls, curie: str) -> Optional[URIRef]:
        prefix, localname = curie.split(':', 1)
        ns = CurieNamespace.catalog.get(prefix, None)
        return ns[localname] if ns else None

    def __new__(cls, prefix: str, ns: Union[str, bytes, URIRef]) -> "CurieNamespace":
        rt = Namespace.__new__(cls, str(ns) if not isinstance(ns, bytes) else ns)
        rt.prefix = prefix
        if prefix in CurieNamespace.catalog:
            if CurieNamespace.catalog[prefix] != str(rt):
                # prefix is bound to a different namespace
                warning(f"Prefix: {prefix} already references {CurieNamespace.catalog[prefix]} - not updated to {rt}")
        else:
            CurieNamespace.catalog[prefix] = rt
        return rt

    def curie(self, reference: Optional[str] = '') -> str:
        return self.prefix + ':' + reference
