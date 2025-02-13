# Currently the main purposing of this makefile is to synchronize
# latest releases of linkml-model into linkml_runtime/linkml_model
#
# See https://github.com/linkml/linkml-runtime/issues/10

# TODO: make this mechanism more robust
MODEL_DIR = ../linkml-model/linkml_model/

update_model:
	cp -pr $(MODEL_DIR)/* linkml_runtime/linkml_model
	sed -i 's/from jsonasobj2/from linkml_runtime.utils.jsonasobj2/g' linkml_runtime/linkml_model/*.py

test:
	poetry run pytest


# temporary measure until linkml-model is synced
linkml_runtime/processing/validation_datamodel.py: linkml_runtime/processing/validation_datamodel.yaml
	gen-python $< > $@.tmp && mv $@.tmp $@
	sed -i 's/from jsonasobj2/from linkml_runtime.utils.jsonasobj2/g' linkml_runtime/processing/validation_datamodel.py
