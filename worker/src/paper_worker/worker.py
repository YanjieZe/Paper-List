from __future__ import annotations

import logging
import signal
import time

from .config import Settings
from .db import Database
from .jobs import handle_job
from .queue import complete_job, fail_job, lease_next_job

logger = logging.getLogger(__name__)


def run_worker(settings: Settings, *, once: bool = False) -> None:
    settings.prepare_runtime()
    database = Database(settings)
    database.open()
    stopping = False

    def stop(*_args) -> None:
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    try:
        while not stopping:
            with database.connection() as conn:
                job = lease_next_job(conn, settings.worker_id, settings.job_lease_seconds)
                if job:
                    try:
                        result = handle_job(conn, settings, job)
                        complete_job(conn, job.id, result)
                    except Exception as error:
                        logger.exception("job %s failed", job.id)
                        fail_job(conn, job, error)
                elif once:
                    break
            if not job:
                time.sleep(settings.poll_interval_seconds)
            if once:
                break
    finally:
        database.close()
