import csv
import re
from abc import ABC, abstractmethod
from json_flattener import unflatten_from_csv, KeyConfig, GlobalConfig, Serializer
import json
from typing import Iterator, Optional, Type, Union, List, TextIO
from linkml_runtime.utils.yamlutils import YAMLRoot
from pydantic import BaseModel

from linkml_runtime.loaders.loader_root import Loader
from linkml_runtime.loaders.json_loader import JSONLoader
from linkml_runtime.linkml_model.meta import SlotDefinitionName, SchemaDefinition, ClassDefinition
from linkml_runtime.utils.yamlutils import YAMLRoot
from linkml_runtime.utils.schemaview import SchemaView
from linkml_runtime.utils.csvutils import get_configmap

class DelimitedFileLoader(Loader, ABC):

    def __init__(self,
                 source: Union[str, dict, TextIO] = None,
                 skip_empty_rows: bool = False,
                 index_slot_name: Optional[str] = None):
        super().__init__(source)
        self.skip_empty_rows = skip_empty_rows
        self.index_slot_name = index_slot_name


    @property
    @abstractmethod
    def delimiter(self):
        pass

    def load_as_dict(self, 
                     source: str,
                     index_slot: SlotDefinitionName = None,
                     schema: SchemaDefinition = None,
                     schemaview: SchemaView = None,
                     **kwargs) -> Union[dict, List[dict]]:
        json_str = self._get_json_str_to_load(source, index_slot, schema, schemaview, **kwargs)
        return JSONLoader().load_as_dict(json_str)

    def load_any(self, *args, **kwargs) -> Union[YAMLRoot, List[YAMLRoot]]:
        return self.load(*args, **kwargs)

    def loads(self, input,
              target_class: Type[Union[BaseModel, YAMLRoot]],
              index_slot: SlotDefinitionName = None,
              schema: SchemaDefinition = None,
              schemaview: SchemaView = None,
              **kwargs) -> str:
        json_str = self._get_json_str_to_load(input, index_slot, schema, schemaview, **kwargs)
        return JSONLoader().loads(json_str, target_class=target_class)

    def load(self, source: str,
             target_class: Type[Union[BaseModel, YAMLRoot]],
             index_slot: SlotDefinitionName = None,
             schema: SchemaDefinition = None,
             schemaview: SchemaView = None,
             **kwargs) -> str:
        json_str = self._get_json_str_to_load(source, index_slot, schema, schemaview, **kwargs)
        return JSONLoader().loads(json_str, target_class=target_class)

    def _get_json_str_to_load(self,
                          input,
                          index_slot: SlotDefinitionName = None,
                          schema: SchemaDefinition = None,
                          schemaview: SchemaView = None,
                          **kwargs):
        if schemaview is None:
            schemaview = SchemaView(schema)
        configmap = get_configmap(schemaview, index_slot)
        config = GlobalConfig(key_configs=configmap, csv_delimiter=self.delimiter)
        objs = unflatten_from_csv(input, config=config, **kwargs)
        return json.dumps({index_slot: objs})

    def _rows(self) -> Iterator[dict]:
        with open(self.source) as file:
            reader: csv.DictReader = csv.DictReader(file, delimiter=self.delimiter, skipinitialspace=True)
            for row in reader:
                if self.skip_empty_rows and not any(row.values()):
                    continue
                yield {k: _parse_numeric(v) for k, v in row.items() if k is not None and v != ""}

    def iter_instances(self) -> Iterator[dict]:
        if self.index_slot_name is not None:
            yield {self.index_slot_name: list(self._rows())}
        else:
            yield from self._rows()

def _parse_numeric(value: str):
    if not isinstance(value, str) or not re.search(r"[0-9]", value):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        pass
    try:
        return float(value)
    except (TypeError, ValueError, OverflowError):
        return value
