#!/usr/bin/env python
import logging

from celery import Celery
from celery.utils.log import get_task_logger

from automappa import settings

logging.basicConfig(
    format="[%(levelname)s] %(name)s: %(message)s",
    level=logging.DEBUG,
)

numba_logger = logging.getLogger("numba")
numba_logger.setLevel(logging.WARNING)
numba_logger.propagate = False
h5py_logger = logging.getLogger("h5py")
h5py_logger.setLevel(logging.WARNING)
h5py_logger.propagate = False
root_logger = logging.getLogger()
root_logger.setLevel(logging.WARNING)

queue = Celery(
    __name__,
    backend=settings.celery.backend_url,
    broker=settings.celery.broker_url,
)

queue.config_from_object("automappa.conf.celeryconfig")
task_logger = get_task_logger(__name__)

if settings.server.debug:
    task_logger.debug(
        f"celery config:\n{queue.conf.humanize(with_defaults=False, censored=True)}"
    )
