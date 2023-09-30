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

### Authentication token

The package provides multiple ways how to supply the authentication token.

#### Ini file

In order for the configuration file to be parsed correctly, create the file following these rules:

- name - `oarepo_upload.ini`
- content template
  ```
  [authentication]
  token = enter-token-here
  ```

The cofiguration file can be located in three different places:
- current directory
- hidden in the home directory
- in the `.config` directory in your home directory

### Record and source dependencies

`Record` represents an entity uploaded to the repository.

`Source` represents an object that generates records limited by given timestamps and can return the size of collection (source is expected to provide an iterator).

The package contains base classes from which the entities mentioned above are derived - `AbstractRecord` and `AbstractRecordSource`.

#### Setup configuration

After deriving concrete record and source classes, configure entry points in the `setup.cfg`.

For example, let's call the created classes `MyRecord` and `MyRecordSource` and put them inside the package itself. Then the entry points should be configured in the following way:

```
[options.entry_points]
...
oarepo_upload_cli.dependencies =
    oarepo_upload_source = oarepo_upload_cli.my_record_source:MyRecordSource
    oarepo_upload_record = oarepo_upload_cli.my_record:MyRecord
```

#### Command line argument

Optionally we can specify path to the custom record and record source via arguments - `record_arg` and `source_arg`.

## Upload script

Options:
- `--collection-url` - Concrete collection URL address to synchronize records.
- `--record_arg` - Record entry point path.
- `--source_arg` - Record source entry point path.
- `--modified_after` - Timestamp that represents date after modification. If not specified, the last updated timestamp from repository will be used.
- `--modified_before` - Timestamp that represents date before modification.
- `--token` - SIS bearer authentication token.
