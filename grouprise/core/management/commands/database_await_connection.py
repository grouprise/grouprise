import logging
import time

from django.core.management.base import BaseCommand
from django.db import connection, OperationalError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Awaits an operational database connection."

    def add_arguments(self, parser):
        parser.add_argument(
            "--retries",
            type=int,
            default=10,
            help="Number of retries before giving up.",
        )
        parser.add_argument(
            "--retry-wait",
            type=int,
            default=2,
            help="Wait times between retries in seconds.",
        )

    def handle(self, retries: int, retry_wait: int, **options):
        last_exc = None
        for num_retry in range(1, retries):
            try:
                connection.ensure_connection()
            except OperationalError as exc:
                last_exc = exc
                num_retries_left = retries - num_retry
                retry_plural = "retries" if num_retries_left > 1 else "retry"
                logging.warning(
                    f"Database connection failed. {num_retries_left} {retry_plural} left. "
                    f"Error was: %s.",
                    str(exc).strip(),
                )
                time.sleep(retry_wait)
            else:
                return
        if last_exc:
            raise last_exc from None
