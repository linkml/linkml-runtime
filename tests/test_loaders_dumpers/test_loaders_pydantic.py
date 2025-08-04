from pathlib import Path

import pytest
from hbreader import FileInfo
from pydantic import BaseModel

import tests.environment as test_base
from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.loaders import json_loader, yaml_loader
from tests.test_loaders_dumpers.environment import env
from tests.test_loaders_dumpers.models.books_normalized_pydantic import BookSeries
from tests.test_loaders_dumpers.models.kitchen_sink_pydantic import Dataset


@pytest.mark.parametrize(
    "filename,model,loader",
    [
        ("book_series_lotr.yaml", BookSeries, yaml_loader),
        ("book_series_lotr.json", BookSeries, json_loader),
        ("kitchen_sink_normalized_inst_01.yaml", Dataset, yaml_loader),
        ("kitchen_sink_normalized_inst_01.json", Dataset, json_loader),
    ],
)
def test_loader_basemodel(filename, model, loader):
    name = Path(filename).stem
    type = Path(filename).suffix.lstrip(".")
    expected_yaml = env.expected_path("load", f"{name}_{type}.yaml")

    metadata = FileInfo()

    python_obj: BaseModel = loader.load(filename, model, metadata=metadata, base_dir=env.indir)
    assert env.eval_single_file(expected_yaml, yaml_dumper.dumps(python_obj))

    # Make sure metadata gets filled out properly using pathlib
    rel_path = Path(test_base.env.cwd).resolve().parent
    base_path = Path(metadata.base_path).resolve()
    source_file = Path(metadata.source_file).resolve()

    assert Path("tests/test_loaders_dumpers/input") == base_path.relative_to(rel_path)
    assert Path(f"tests/test_loaders_dumpers/input/{filename}") == source_file.relative_to(rel_path)
