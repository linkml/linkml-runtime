from io import StringIO
from typing import Dict, Optional, TextIO, Type, Union

import click
import yaml
from hbreader import FileInfo
from linkml_runtime.loaders.loader_root import Loader
from linkml_runtime.utils.yamlutils import DupCheckYamlLoader, YAMLRoot


class YAMLLoader(Loader):

    def load(self, source: Union[str, dict, TextIO], target_class: Type[YAMLRoot], *, base_dir: Optional[str] = None,
             metadata: Optional[FileInfo] = None, **_) -> YAMLRoot:
        def loader(data: Union[str, dict], _: FileInfo) -> Optional[Dict]:
            return yaml.load(StringIO(data), DupCheckYamlLoader) if isinstance(data, str) else data

        if not metadata:
            metadata = FileInfo()
        if base_dir and not metadata.base_path:
            metadata.base_path = base_dir
        return self.load_source(source, loader, target_class, accept_header="text/yaml, application/yaml;q=0.9",
                                metadata=metadata)

    
@click.group()
def cli():
    pass
@cli.command('yaml_load')
@click.option('-i', '--input', help='Data source that needs to be loaded.')
@click.option('-t', '--target', help=' Target class')
@click.option('b', '--base-dir', help='Base directory (optional)')
@click.option('-m', '--metadata', help='Metadata (optional)')


def load_click(input:str, target:str, base_dir:str, metadata:str) -> YAMLRoot:
    """Loads data from source

    Args:

        input (str): Input data to load

        target (str): Target Class

        base_dir (str): Base directory

        metadata (str): Metadata

    Returns:

        YAMLRoot
    """
    YAMLLoader.load(source=input, target_class=target, base_dir=base_dir, metadata=metadata)

if __name__ == '__main__':
    cli()
