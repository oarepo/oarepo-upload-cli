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

- name - `~/.repository-uploader.ini`
- content template
  ```
  [authentication]
  token = enter-token-here

  [repository]
  collection_url = url_of_the_collection
  record_modified_field = dateModified
  file_modified_field = dateModified

  [entrypoints]
  # name of the entrypoint inside oarepo_upload_cli.dependencies 
  # that gives implementation of RecordSource
  source = 

    # name of the entrypoint inside oarepo_upload_cli.dependencies 
  # that gives implementation of RepositoryClient
  repository = 
    ```

#### Environment variables

Values in the configuration can be overriden by these environment variables:

```bash
REPOSITORY_UPLOADER_BEARER_TOKEN

REPOSITORY_UPLOADER_COLLECTION_URL
REPOSITORY_UPLOADER_FILE_MODIFIED_FIELD_NAME
REPOSITORY_UPLOADER_RECORD_MODIFIED_FIELD_NAME

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

