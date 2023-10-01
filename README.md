# oarepo-upload-cli

Package that synchronizes documents between the student system and repository up to some date.

## CLI Usage

To use the upload CLI tool, you first have to install the package somewhere.

### Installing upload CLI in a separate virtualenv

Create a separate virtualenv and install upload CLI into it:

```
python3.10 -m venv .venv-upload-cli
(source .venv-upload-cli/bin/activate; pip install -U pip setuptools wheel; pip install oarepo-upload-cli)
```

### Configuration

#### Ini file

In order for the configuration file to be parsed correctly, create the file following these rules:

- name - `~/.repository-uploader.ini` (or anywhere else using --config param)
- content template
  ```ini
  [authentication]
  token = enter-token-here

  [repository]
  collection_url = url_of_the_collection

  # use dot notation to select the metadata field. Note that this should not be the repository's
  # modified but a different field that will reflect the modified attribute of your source record
  record_modified_field = metadata.dateModified
  file_modified_field = metadata.dateModified

  # field inside the record that holds the id from the source  
  id_query_field = metadata.originalId
  
  # to be able to upload only non-modified records, provide a max(..) aggregation
  # inside the repository and set the path within the aggs element here
  last_modification_date_agg = dateModifiedAgg.value

  
  
  [entrypoints]
  # name of the entrypoint inside oarepo_upload_cli.dependencies 
  # that gives implementation of RecordSource
  source = 

  # name of the entrypoint inside oarepo_upload_cli.dependencies that gives implementation 
  # of RepositoryClient. In most cases, not need to specify it
  repository = 
    ```

#### Environment variables

Values in the configuration can be overriden by these environment variables:

```bash
REPOSITORY_UPLOADER_BEARER_TOKEN

REPOSITORY_UPLOADER_COLLECTION_URL
REPOSITORY_UPLOADER_FILE_MODIFIED_FIELD_NAME
REPOSITORY_UPLOADER_RECORD_MODIFIED_FIELD_NAME
REPOSITORY_UPLOADER_ID_QUERY_FIELD
REPOSITORY_UPLOADER_LAST_MODIFICATION_DATE_AGG

REPOSITORY_UPLOADER_SOURCE
REPOSITORY_UPLOADER_REPOSITORY
```

#### Command-line options

Commandline options take the highest priority:

```bash
oarepo_upload 
   --config config-file-location
   --token  bearer_token
   --collection-url  collection-url
   --file-modified-field file-modified-field
   --record-modified-field record-modified-field
   --source source-entrypoint
   --repository repository-entrypoint
```

The following options handle which records should be uploaded:
- `--modified_after` - Timestamp that represents date after modification. If not specified, the last updated timestamp from repository will be used.
- `--modified_before` - Timestamp that represents date before modification.

### Implementing Source of records

**Step 1:** Before calling the client, you have to implement your own source of records. To do so, inherit from 
`RecordSource`:

```python
from oarepo_upload_cli.source import RecordSource, SourceRecord, SourceRecordFile
from oarepo_upload_cli.config import Config


class MySource(RecordSource):
  """
  Describes a source that is used to generate records.
  """

  def __init__(self, config: Config) -> None:
    self._config = config

  def get_records(self, modified_after, modified_before):
    for rec in backend.records(modified_after, modified_before):
      yield SourceRecord(
        record_id=rec.id,
        datetime_modified=rec.modified,
        deleted=rec.deleted,
        # make sure that the metadata include datetimeModified
        # or whatever the modified record name is in config
        metadata=rec.metadata.as_json(),
        files=[
          SourceRecordFile(
            key=f.filename,
            content_type='application/octet-stream',  # use always this
            datetime_modified=f.modified,
            metadata={
              # always include the datetimeModified inside the metadata
              # or whatever the modified field name is in config
              'datetimeModified': f.modified.isoformat()
            },
            reader=lambda: f.open_for_read()
          ) for f in rec.files
        ]
      )

  def get_records_count(self, modified_after, modified_before):
    return backend.records_changed_count(modified_after, modified_before) 
```

**Step 1:** Register the implementation to entrypoints:

```cfg
[options.entry_points]

oarepo_upload_cli.dependencies =
    my_source = "my_source_module:MySource"
```

**Step 3:** Run the client with `--source=my_source` or put then source to configuration.