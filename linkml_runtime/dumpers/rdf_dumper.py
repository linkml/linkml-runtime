import json
from typing import Optional

import click
from hbreader import hbread
from linkml_runtime.dumpers.dumper_root import Dumper
from linkml_runtime.utils.context_utils import (CONTEXT_TYPE,
                                                CONTEXTS_PARAM_TYPE)
from linkml_runtime.utils.yamlutils import YAMLRoot
from pyld.jsonld import expand
from rdflib import Graph
from rdflib_pyld_compat import rdflib_graph_from_pyld_jsonld


class RDFDumper(Dumper):
    def as_rdf_graph(self, element: YAMLRoot, contexts: CONTEXTS_PARAM_TYPE, namespaces: CONTEXT_TYPE = None) -> Graph:
        """
        Convert element into an RDF graph guided by the context(s) in contexts
        :param element: element to represent in RDF
        :param contexts: JSON-LD context(s) in the form of:
            * file name
            * URL
            * JSON String
            * dict
            * JSON Object
            * A list containing elements of any type named above
        :param namespaces: A file name, URL, JSON String, dict or JSON object that includes the set of namespaces to
        be bound to the return graph.  If absent, contexts get used
        :return: rdflib Graph containing element
        """
        if isinstance(contexts, list):
            inp_contexts = [json.loads(hbread(c)) for c in contexts]
        else:
            inp_contexts = json.loads(hbread(contexts))

        from linkml_runtime.dumpers import json_dumper
        rdf_jsonld = expand(json_dumper.dumps(element), options=dict(expandContext=inp_contexts))
        g = rdflib_graph_from_pyld_jsonld(rdf_jsonld)

        if namespaces is not None:
            ns_source = json.loads(hbread(namespaces))
        else:
            ns_source = inp_contexts

        # TODO: make a utility out of this or add it to prefixcommons
        if ns_source and '@context' in ns_source:
            ns_contexts = ns_source['@context']
            if isinstance(ns_contexts, dict):
                ns_contexts = [ns_contexts]
            for ns_context in ns_contexts:
                if isinstance(ns_context, dict):
                    for pfx, ns in ns_context.items():
                        if isinstance(ns, dict):
                            if '@id' in ns and ns.get('@prefix', False):
                                ns = ns['@id']
                            else:
                                continue
                        if not pfx.startswith('@'):
                            g.bind(pfx, ns)

        return g

    def dump(self, element: YAMLRoot, to_file: str, contexts: CONTEXTS_PARAM_TYPE = None, fmt: str = 'turtle') -> None:
        """
        Write element as rdf to to_file
        :param element: LinkML object to be emitted
        :param to_file: file to write to
        :param contexts: JSON-LD context(s) in the form of:
            * file name
            * URL
            * JSON String
            * dict
            * JSON Object
            * A list containing elements of any type named above
        :param fmt: RDF format
        """
        super().dump(element, to_file, contexts=contexts, fmt=fmt)

    def dumps(self, element: YAMLRoot, contexts: CONTEXTS_PARAM_TYPE = None, fmt: Optional[str] = 'turtle') -> str:
        """
        Convert element into an RDF graph guided by the context(s) in contexts
        :param element: element to represent in RDF
        :param contexts: JSON-LD context(s) in the form of a file or URL, a json string or a json obj
        :param fmt: RDF format
        :return: rdflib Graph containing element
        """
        return self.as_rdf_graph(element, contexts).serialize(format=fmt).decode()

@click.group()
def cli():
    pass

@cli.command('as_rdf_graph')
@click.option('-e', '--element', help='LinkML object to be emitted.')
@click.option('-c', '--contexts', help='JSON-LD context(s)')
@click.option('-n', '--namespaces', help='A file name, URL, JSON String, dict or JSON object that includes the set of namespaces to \
        be bound to the return graph.  If absent, contexts get used')
def as_rdf_graph_cli(element: YAMLRoot, contexts: CONTEXTS_PARAM_TYPE, namespaces: CONTEXT_TYPE = None) -> Graph:
    """Convert element into an RDF graph guided by the context(s) in contexts. \n

    Args: \n
        element (YAMLRoot): Element to represent in RDF. \n
        contexts (CONTEXTS_PARAM_TYPE): JSON-LD context(s). \n
        namespaces (CONTEXT_TYPE, optional): A file name, URL, JSON String, dict or JSON object that includes the set of namespaces to
        be bound to the return graph.  If absent, contexts get used. Defaults to None. \n

    Returns: \n
        Graph: rdflib Graph containing element. \n
    """
    RDFDumper.as_rdf_graph(element=element, contexts=contexts, namespaces=namespaces)


@cli.command('rdf_dump')
@click.option('-e', '--element', help='LinkML object to be serialized as YAML.')
@click.option('-t', '--to-file', help='File to write to')
@click.option('-c', '--contexts', help='JSON-LD context(s)')
@click.option('-f', '--fmt', default= 'turtle', help='Rdf format')

def dump_cli(element:YAMLRoot, to_file:str, fmt:str, contexts:CONTEXTS_PARAM_TYPE = None) -> None:
    """Write element as rdf to to_file. \n

    Args: \n
        element (YAMLRoot): Element to represent in RDF. \n
        to_file (str): File to write to. \n
        fmt (str): RDF format \n
        contexts (CONTEXTS_PARAM_TYPE, optional): JSON-LD context(s) in the form of: \n
            * file name \n
            * URL \n
            * JSON String \n
            * dict \n
            * JSON Object \n
            * A list containing elements of any type named above.  \n
            Defaults to None. \n
    """
    RDFDumper.dump(element=element, to_file=to_file, contexts=contexts, fmt=fmt)

@cli.command('rdf_dumps')
@click.option('-e', '--element', help='LinkML object to be emitted.')
@click.argument('contexts', required=True)
@click.option('-f', '--fmt', default= 'turtle', help='Rdf format')

def dumps_cli(element:YAMLRoot, fmt:str, contexts:CONTEXTS_PARAM_TYPE = None) -> str:
    """Convert element into an RDF graph guided by the context(s) in contexts. \n

    Args: \n
        element (YAMLRoot): Element to represent in RDF. \n
        fmt (str): RDF format \n
        contexts (CONTEXTS_PARAM_TYPE, optional): JSON-LD context(s) in the form of a file or URL, a json string or a json obj. \n
        Defaults to None. \n

    Returns: \n
        str: RDFLib Graph containing element.
    """
    RDFDumper.dumps(element=element, contexts=contexts, fmt=fmt)

if __name__ == '__main__':
    cli()
