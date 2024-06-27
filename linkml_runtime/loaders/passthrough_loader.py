from typing import Any, Iterator

from linkml_runtime.loaders.loader_root import Loader


class PassthroughLoader(Loader):
    """A loader that passes through from an existing Iterator

    :param source: An Iterator
    """

    def __init__(self, source: Iterator) -> None:
        super().__init__(source)

    def iter_instances(self) -> Iterator[Any]:
        """Pass through instances from an Iterator

        :return: Iterator over data instances
        :rtype: Iterator[Any]
        """
        yield from self.source

    def load_any(self, *args, **kwargs):
        raise NotImplementedError('Passthrough loader doesnt actually load anything')