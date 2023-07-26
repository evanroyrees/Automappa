#!/usr/bin/env python
import time

from automappa.tasks import queue


@queue.task(bind=True)
def set_badge_color(self, color: str) -> str:
    time.sleep(15)
    return color


if __name__ == "__main__":
    pass
