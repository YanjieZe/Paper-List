from __future__ import annotations

import json
import logging
from pathlib import Path

import typer

from .config import get_settings
from .db import Database
from .evals import validate_eval_manifest
from .legacy import import_legacy_catalog, persist_legacy_records, scan_legacy
from .projections import generate_topic_views
from .worker import run_worker

app = typer.Typer(no_args_is_help=True, help="Paper-List Research OS worker")


@app.command()
def migrate(migrations: Path = Path("database/migrations")) -> None:
    """Apply PostgreSQL migrations exactly once."""
    settings = get_settings()
    database = Database(settings)
    database.open()
    try:
        applied = database.migrate(migrations)
    finally:
        database.close()
    typer.echo(json.dumps({"applied": applied}, indent=2))


@app.command("legacy-scan")
def legacy_scan(
    root: Path = Path("."),
    output: Path | None = None,
    persist: bool = False,
) -> None:
    """Account for every URL in README and legacy topic files."""
    report = scan_legacy(root.resolve())
    data = report.model_dump_json(indent=2)
    if output:
        output.write_text(data + "\n", encoding="utf-8")
    if persist:
        settings = get_settings()
        database = Database(settings)
        database.open()
        try:
            with database.connection() as conn:
                inserted = persist_legacy_records(conn, report)
        finally:
            database.close()
        typer.echo(json.dumps({"inserted": inserted, "discovered": report.discovered_urls}))
    else:
        typer.echo(data)


@app.command("legacy-import")
def legacy_import(root: Path = Path(".")) -> None:
    """Create one candidate Research Item per normalized legacy URL and audit every occurrence."""
    report = scan_legacy(root.resolve())
    settings = get_settings()
    database = Database(settings)
    database.open()
    try:
        with database.connection() as conn:
            result = import_legacy_catalog(conn, report)
    finally:
        database.close()
    typer.echo(json.dumps(result, indent=2))


@app.command("generate-topics")
def generate_topics(root: Path = Path(".")) -> None:
    """Regenerate public topic projections from PostgreSQL metadata."""
    settings = get_settings()
    database = Database(settings)
    database.open()
    try:
        with database.connection() as conn:
            result = generate_topic_views(conn, root.resolve())
    finally:
        database.close()
    typer.echo(json.dumps(result, indent=2))


@app.command("eval-contracts")
def eval_contracts(root: Path = Path(".")) -> None:
    """Validate golden-set coverage before running paid evaluation jobs."""
    typer.echo(json.dumps(validate_eval_manifest(root.resolve()), indent=2))


@app.command("run")
def run(once: bool = False) -> None:
    """Poll PostgreSQL and execute durable background jobs."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run_worker(get_settings(), once=once)


if __name__ == "__main__":
    app()
