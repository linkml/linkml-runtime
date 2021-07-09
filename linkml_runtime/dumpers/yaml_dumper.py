import click
import yaml
from linkml_runtime.dumpers.dumper_root import Dumper
from linkml_runtime.utils.yamlutils import YAMLRoot


class YAMLDumper(Dumper):

    def dumps(self, element: YAMLRoot, **kwargs) -> str:
        """ Return element formatted as a YAML string """
        return yaml.dump(element, Dumper=yaml.SafeDumper, sort_keys=False, **kwargs)


@click.group()
def cli():
    pass
@cli.command(name='yaml_dumps', context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
))
@click.option('-e', '--element', help='LinkML object to be emitted.')
@click.pass_context
def dumps_cli(ctx, element:YAMLRoot) -> str:
    """Return element as a JSON or a JSON-LD string \n
    Args: \n
        element (YAMLRoot): LinkML object to be emitted. \n
        contexts (CONTEXTS_PARAM_TYPE, optional): JSON-LD context(s) in the form of: \n
            * file name \n
            * URL \n
            * JSON String \n
            * dict \n
            * JSON Object \n
            * A list containing elements of any type named above. \n
    Returns: \n
        JSON Object representing the element.
    """
    extra_args = {ctx.args[i].lstrip('-'): ctx.args[i+1] for i in range(0, len(ctx.args), 2)}
    
    YAMLDumper.dumps(element=element, kwargs=extra_args)

if __name__ == '__main__':
    cli()