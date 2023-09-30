black oarepo_upload_cli tests --target-version py310
autoflake --in-place --remove-all-unused-imports --recursive oarepo_upload_cli tests
isort oarepo_upload_cli tests  --profile black
