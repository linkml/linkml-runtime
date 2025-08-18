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

LOADER = {"yaml": yaml_loader, "json": json_loader}


@pytest.mark.parametrize("format", list(LOADER.keys()))
@pytest.mark.parametrize(
    ("filename", "model"),
    [
        ("book_series_lotr", BookSeries),
        ("kitchen_sink_normalized_inst_01", Dataset),
    ],
)
def test_loader_base_model(filename, model, format):
    loader = LOADER[format]
    expected_yaml = env.expected_path("load", f"{filename}_{format}.yaml")
    exp_yaml_path = Path(expected_yaml)
    exp_path = Path(env.outdir) / "load" / f"{filename}_{format}.yaml"
    assert exp_path.as_posix() == exp_yaml_path.as_posix()

    assert Path(env.indir).exists()
    assert Path(env.outdir).exists()

    assert exp_path.exists()
    assert exp_yaml_path.exists()

    metadata = FileInfo()

    python_obj: BaseModel = loader.load(f"{filename}.{format}", model, metadata=metadata, base_dir=env.indir)

    # temporary insert for debugging
    with open(expected_yaml) as expf:
        expected = expf.read()
    got = yaml_dumper.dumps(python_obj)
    expected_trimmed = expected.replace("\r\n", "\n").strip()
    got_trimmed = got.replace("\r\n", "\n").strip()
    assert expected_trimmed == got_trimmed
    # end insert

    assert env.eval_single_file(expected_yaml, yaml_dumper.dumps(python_obj))

    # Make sure metadata gets filled out properly using pathlib
    rel_path = Path(test_base.env.cwd).resolve().parent
    base_path = Path(metadata.base_path).resolve()
    source_file = Path(metadata.source_file).resolve()

    assert Path("tests/test_loaders_dumpers/input") == base_path.relative_to(rel_path)
    assert Path(f"tests/test_loaders_dumpers/input/{filename}.{format}") == source_file.relative_to(rel_path)
