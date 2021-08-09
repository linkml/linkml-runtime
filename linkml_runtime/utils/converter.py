import os
import re
import sys
from types import ModuleType

import click

from linkml_runtime.utils.compile_python import compile_python

from linkml_runtime.dumpers.yaml_dumper import YAMLDumper
from linkml_runtime.dumpers.json_dumper import JSONDumper
from linkml_runtime.dumpers.rdf_dumper import RDFDumper
from linkml_runtime.dumpers.dumper_root import Dumper
from linkml_runtime.loaders.yaml_loader import YAMLLoader
from linkml_runtime.loaders.json_loader import JSONLoader
from linkml_runtime.loaders.rdf_loader import RDFLoader
from linkml_runtime.loaders.loader_root import Loader

dumpers_loaders = {
    'yaml': (YAMLDumper, YAMLLoader),
    'json': (JSONDumper, JSONLoader),
    'rdf': (RDFDumper, RDFLoader),
}

def _get_format(input: str, input_format: str =None):
    if input_format is None:
        if input is None:
            raise Exception(f'Must pass format option OR pass a filename with known file suffix')
        _, ext = os.path.splitext(input)
        if ext is not None:
            input_format = ext.replace('.', '')
        else:
            raise Exception(f'Must pass format option OR use known file suffix: {input}')
    return input_format.lower()

def get_loader(fmt: str) -> Loader:
    return dumpers_loaders[fmt][1]()
def get_dumper(fmt: str) -> Loader:
    return dumpers_loaders[fmt][0]()


@click.command()
@click.option("--module", "-m",
              help="Path to python datamodel module")
@click.option("--output", "-o",
              help="Path to output file")
@click.option("--input-format", "-f",
              type=click.Choice(list(dumpers_loaders.keys())),
              help="Input format. Inferred from input suffix if not specified")
@click.option("--output-format", "-t",
              type=click.Choice(list(dumpers_loaders.keys())),
              help="Output format. Inferred from output suffix if not specified")
@click.option("--target-class", "-C",
              required=True,
              help="name of class in datamodel that the root node instantiates")
@click.option("--context", "-c",
              multiple=True,
              help="path to JSON-LD context file. Required for RDF input/output")
@click.argument("input")
def cli(input, module, target_class, context=None, output=None, input_format=None, output_format=None, index_slot=None, schema=None) -> None:
    """
    Converts instance data to and from different LinkML Runtime serialization formats.

    The instance data must conform to a LinkML model, and there must be python dataclasses
    generated from that model. The converter works by first using a linkml-runtime loader to
    instantiate in-memory model objects, then dumpers are used to serialize.

    When converting to or from RDF, a JSON-lD context must also be passed
    """
    python_module = compile_python(module)
    target_class = python_module.__dict__[target_class]
    input_format = _get_format(input, input_format)
    output_format = _get_format(output, output_format)
    loader = get_loader(input_format)
    dumper = get_dumper(output_format)
    inargs = {}
    outargs = {}
    if input_format == 'rdf':
        if context is None:
            raise Exception('Must pass in context for RDF input')
        inargs['contexts'] = list(context)
    if output_format == 'rdf':
        if context is None:
            raise Exception('Must pass in context for RDF output')
        outargs['contexts'] = list(context)

    obj = loader.load(source=input,  target_class=target_class, **inargs)
    if output is not None:
        dumper.dump(obj, output, **outargs)
    else:
        print(dumper.dumps(obj, **outargs))


if __name__ == '__main__':
    cli(sys.argv[1:])
