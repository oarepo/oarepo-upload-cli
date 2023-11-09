from pathlib import Path

import arrow
import click
from tqdm import tqdm

from oarepo_upload_cli.audit import Audit, AuditLevel
from oarepo_upload_cli.config import Config
from oarepo_upload_cli.entry_points_loader import EntryPointsLoader
from oarepo_upload_cli.source import SourceRecord
from oarepo_upload_cli.uploader import Uploader


@click.command()
@click.option(
    "--config",
    "config_name",
    help="Configuration entry point path of config implementation.",
)
@click.option(
    "--source",
    "source_name",
    help="Configuration entry point path of source implementation.",
)
@click.option(
    "--repository",
    "repository_name",
    help="Configuration entry point path of repository client implementation.",
)
@click.option("--token", "token", help="Bearer token")
@click.option("--collection-url", "collection_url", help="Collection url")
@click.option(
    "--record-modified-field",
    "record_modified_field",
    help="Path to field containing record modification date",
)
@click.option(
    "--file-modified-field",
    "file_modified_field",
    help="Path to field containing file modification date",
)
@click.option(
    "--modified_after",
    help="Timestamp that represents date after modification. "
    "If not specified, the last updated timestamp from repository will be used.",
)
@click.option(
    "--modified_before", help="Timestamp that represents date before modification."
)
@click.option("--dry-run/--no-dry-run", help="Dry run - do not upload anything")
@click.option("--suppress-warnings/--no-suppress-warnings")
@click.option("-v", "--verbose", count=True)
@click.option("--audit-file")
def main(
    config_name,
    source_name,
    repository_name,
    modified_after,
    modified_before,
    dry_run,
    suppress_warnings,
    token,
    collection_url,
    record_modified_field,
    file_modified_field,
    verbose,
    audit_file,
) -> None:
    if suppress_warnings:
        import warnings

        warnings.filterwarnings("ignore")

    audit = Audit(AuditLevel.ERROR, audit_file=audit_file)
    audit.set_verbosity(verbose)

    # -----------------
    # - Configuration -
    # -----------------
    ep_loader = EntryPointsLoader()
    config_class = ep_loader.load_entry_point(
        config_name,
        default=Config,
    )
    config = config_class(str(Path.home() / ".repository-uploader.ini"))
    config.override("authentication", "token", token)
    config.override("entrypoints", "source", source_name)
    config.override("entrypoints", "repository", repository_name)
    config.override("repository", "collection_url", collection_url)
    config.override("repository", "record_modified_field", record_modified_field)
    config.override("repository", "file_modified_field", file_modified_field)

    # --------------------------------
    # - Source and repository client -
    # --------------------------------
    source = ep_loader.load_entry_point(config.source_name)(config, audit)
    repository = ep_loader.load_entry_point(config.repository_name)(
        config, audit=audit, dry_run=dry_run
    )

    # --------------
    # - Timestamps -
    # --------------
    if modified_before:
        modified_before = arrow.get(modified_before).datetime.replace(tzinfo=None)

    if modified_after:
        modified_after = arrow.get(modified_after).datetime.replace(tzinfo=None)

    # ----------
    # - Upload -
    # ----------

    if verbose and not audit_file:
        progress_bar = tqdm(disable=True)
    else:
        progress_bar = tqdm()

    def callback(source_record: SourceRecord, cnt, approximate_count, message):
        if progress_bar.total != approximate_count:
            progress_bar.total = approximate_count
        progress_bar.set_description(
            f"{source_record.record_id} {source_record.datetime_modified} {message}"
        )
        progress_bar.update(cnt - progress_bar.n)

    uploader = Uploader(config, source, repository)
    uploader.upload(modified_after, modified_before, callback)


if __name__ == "__main__":
    main()
