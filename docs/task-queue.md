# Tasks

Simple steps to adding a task:

1. [Add page's `tasks` module](#adding-a-new-task-module-discovery-path)
2. [Add page tasks module in `celeryconfig.py`](#add-in-tasks-module-in-celeryconfigpy)
3. [Define task in `tasks` module](#define-task-in-tasks-module)
4. [Import task in `__init__.py` w.r.t `tasks` module](#import-task-in-__init__py-within-respective-tasks-module)


## Adding a new task module discovery path

To have the Celery task-queue register a page's tasks, they must be
discovered based on the relative task module's path. Here's a simple example 
(It may be easier to show here than explain...)

We have our page's tasks module:

```console
automappa/pages/home/tasks
|...
├── __init__.py
└── status_badge.py
```

## Add in `tasks` module in `celeryconfig.py`

We configure celery for this module in the `celeryconfig.py` file.

```python
# contents of automappa/conf/celeryconfig.py
imports = ("automappa.pages.home.tasks", "automappa.tasks")
```

This ***almost*** takes care of celery checking for tasks in the module

Unfortunately, this is not all...

## Define task in `tasks` module

Here is a simple example where we will simulate a long-running task with sleep and then set a badge color.

> Notice we are importing our celery task-queue application (`queue`) from the base automappa directory.

```python
# contents of /automappa/pages/home/tasks/status_badge.py
import time

from automappa.tasks import queue


@queue.task(bind=True)
def set_badge_color(self, color: str) -> str:
    time.sleep(15)
    return color


if __name__ == "__main__":
    pass

```

Now with our task defined we can move on to importing it into our `tasks` module to be used by celery.

## Import task in `__init__.py` within respective `tasks` module

We also need to update the
`automappa/pages/home/tasks/__init__.py` with all of our implemented tasks in the 
module for celery to recognize and register the tasks under the `automappa/pages/home/tasks` module.

For example  we have a task `set_badge_color` defined in `status_badge.py`.

We would need to explicitly add this task to `__init__.py` like so:

```python
# contents of `automappa/pages/home/tasks/__init__.py`
from .status_badge import set_badge_color # *Notice this is a relative import*

__all__ = ["set_badge_color"]
```

Voilá, now celery will recognize the task on startup. It should look like this:

<details>

<summary>Celery Startup with `set_badge_color` registered </summary>

```console
 
 -------------- celery@4bbb963e90ec v5.3.1 (emerald-rush)
--- ***** ----- 
-- ******* ---- Linux-5.15.49-linuxkit-pr-x86_64-with-glibc2.31 2023-07-13 18:24:15
- *** --- * --- 
- ** ---------- [config]
- ** ---------- .> app:         automappa.tasks:0x7f23e6d778e0
- ** ---------- .> transport:   amqp://user:**@rabbitmq:5672//
- ** ---------- .> results:     redis://redis:6379/0
- *** --- * --- .> concurrency: 2 (prefork)
-- ******* ---- .> task events: ON
--- ***** ----- 
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery
                
[tasks]
  . automappa.pages.home.tasks.status_badge.set_badge_color
  . automappa.tasks.aggregate_embeddings
  . automappa.tasks.count_kmer
  . automappa.tasks.embed_kmer
  . automappa.tasks.get_embedding_traces_df
  . automappa.tasks.normalize_kmer
  . automappa.tasks.preprocess_clusters_geom_medians
  . automappa.tasks.preprocess_marker_symbols
[2023-07-13 18:24:16,437: INFO/MainProcess] Connected to amqp://user:**@rabbitmq:5672//
[2023-07-13 18:24:16,455: INFO/MainProcess] mingle: searching for neighbors
[2023-07-13 18:24:17,569: INFO/MainProcess] mingle: all alone
[2023-07-13 18:24:17,627: INFO/MainProcess] celery@4bbb963e90ec ready.
```

</details>

## Adding a new task to an existing page

Celery has trouble discovering newly implemented tasks

Unfortunately I have not found a convenient workaround for this
but each page has its own `tasks` module with an `__init__.py` 
where any tasks implemented under this module must be imported into
`__init__.py` and specified in the `__all__` dunder variable.

You can avoid alot of headache by recalling this...
