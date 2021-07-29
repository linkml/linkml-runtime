from linkml_solr.utils.dict_denormalizer import flatten_to_csv, unflatten_from_csv, KeyConfig, GlobalConfig, CONFIGMAP, Serializer
import yaml
import json
import io
from typing import Type
from linkml_runtime.utils.yamlutils import YAMLRoot

from linkml_runtime.dumpers.dumper_root import Dumper
from linkml_runtime.loaders.loader_root import Loader
from linkml_runtime.dumpers import json_dumper
from linkml_runtime.loaders import json_loader
from linkml_runtime.linkml_model.meta import SlotDefinitionName, SchemaDefinition, ClassDefinition
from linkml_runtime.utils.yamlutils import YAMLRoot

def get_configmap(schema: SchemaDefinition, index_slot: SlotDefinitionName) -> CONFIGMAP:
    """

    :param schema: LinkML schema
    :param index_slot: key that indexes the top level object
    :return: mapping between top level keys and denormalization configurations
    """
    if index_slot is not None and schema is not None:
        slot = schema.slots[index_slot]
        if slot.range is not None and slot.range in schema.classes:
            tgt_cls = schema.classes[slot.range]
            print(f'TGT ={tgt_cls.name} => {tgt_cls.slots}')
            cm = {}
            for sn in tgt_cls.slots:
                config = _get_key_config(schema, tgt_cls, sn)
                if config is not None:
                    cm[sn] = config
            return cm
        else:
            logging.warn(f'Slot range not to class: {slot.range}')
    else:
        logging.warn(f'Index slot or schema not specified')
    return {}

def _get_key_config(schema: SchemaDefinition, tgt_cls: ClassDefinition, sn: SlotDefinitionName, sep='_'):
    slot = schema.slots[sn]
    range = slot.range
    if range in schema.classes and slot.inlined:
        range_class = schema.classes[range]
        mappings = {}
        is_complex = False
        for inner_sn in range_class.slots:
            denormalized_sn = f'{sn}{sep}{inner_sn}'
            mappings[inner_sn] = denormalized_sn
            inner_slot = schema.slots[inner_sn]
            inner_slot_range = inner_slot.range
            if (inner_slot_range in schema.classes and inner_slot.inlined) or inner_slot.multivalued:
                is_complex = True
        if is_complex:
            serializers = [Serializer.json]
        else:
            serializers = []
        return KeyConfig(is_list=slot.multivalued, delete=True, flatten=True, mappings=mappings, serializers=serializers)
    else:
        return None


class CSVDumper(Dumper):

    def dumps(self, element: YAMLRoot,
              index_slot: SlotDefinitionName = None,
              schema: SchemaDefinition = None,
              **kwargs) -> str:
        """ Return element formatted as CSV lines """
        element_j = json.loads(json_dumper.dumps(element))
        objs = element_j[index_slot]
        print(f'O={type(objs[0])}')
        configmap = get_configmap(schema, index_slot)
        config = GlobalConfig(key_configs=configmap)
        print(f'CM={configmap}')
        output = io.StringIO()
        flatten_to_csv(objs, output, config=config, **kwargs)
        return output.getvalue()

class CSVLoader(Loader):

    def loads(self, input,
              target_class: Type[YAMLRoot],
              index_slot: SlotDefinitionName = None,
              schema: SchemaDefinition = None,
              **kwargs) -> str:
        configmap = get_configmap(schema, index_slot)
        config = GlobalConfig(key_configs=configmap)
        objs = unflatten_from_csv(input, config=config, **kwargs)
        return json_loader.loads(json.dumps({index_slot: objs}), target_class=target_class)

    def load(self, source: str,
              target_class: Type[YAMLRoot],
              index_slot: SlotDefinitionName = None,
              schema: SchemaDefinition = None,
              **kwargs) -> str:
        configmap = get_configmap(schema, index_slot)
        config = GlobalConfig(key_configs=configmap)
        print(f'Loading from {source}')
        objs = unflatten_from_csv(source, config=config, **kwargs)
        return json_loader.loads(json.dumps({index_slot: objs}), target_class=target_class)


