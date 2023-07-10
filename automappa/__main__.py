#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging


from automappa import settings
from automappa.components import layout
from automappa.data.database import create_db_and_tables
from automappa.app import app

logging.basicConfig(
    format="[%(levelname)s] %(name)s: %(message)s",
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)
numba_logger = logging.getLogger("numba")
numba_logger.setLevel(logging.WARNING)
numba_logger.propagate = False
h5py_logger = logging.getLogger("h5py")
h5py_logger.setLevel(logging.WARNING)
h5py_logger.propagate = False
root_logger = logging.getLogger()
root_logger.setLevel(logging.WARNING)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Automappa: An interactive interface for exploration of metagenomes",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--storage-type",
        help=(
            "The type of the web storage. (default: %(default)s)\n"
            "- memory: only kept in memory, reset on page refresh.\n"
            "- session: data is cleared once the browser quit.\n"
            "- local: data is kept after the browser quit.\n"
        ),
        choices=["memory", "session", "local"],
        default="session",
    )
    parser.add_argument(
        "--clear-store-data",
        help=(
            "Clear storage data (default: %(default)s)\n"
            "(only required if using 'session' or 'local' for `--storage-type`)"
        ),
        action="store_true",
        default=False,
    )
    args = parser.parse_args()

    create_db_and_tables()
    app.layout = layout.render(app, args.storage_type, args.clear_store_data)
    app.run(
        host=settings.server.host,
        port=settings.server.port,
        debug=settings.server.debug,
    )


if __name__ == "__main__":
    main()
