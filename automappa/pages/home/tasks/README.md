# Tasks

## Adding a new task module discovery path

To have the Celery task-queue register a page's tasks, they must be
discovered based on the relative task module's path. Here's a simple example 
(It may be easier to show here than explain...)

We have our page's tasks module:

```console
automappa/pages/home/tasks
├── README.md
├── __init__.py
└── task_status_badge.py
```

We configure celery for this module in the `celeryconfig.py` file.

```python
# contents of celeryconfig.py
imports = ("automappa.pages.home.tasks", "automappa.tasks")
```

This ***almost*** takes care of celery checking for tasks in the module

Unfortunately, this is not all, we also need to update the
`automappa/pages/home/tasks/__init__.py` with all of our implemented tasks in the 
module for celery to recognize and register the tasks under the `automappa/pages/home/tasks` module.

For example  we have a task `set_badge_color` defined in `task_status_badge.py`.

We would need to explicitly add this task to `__init__.py` like so:

```python
# contents of `automappa/pages/home/tasks/__init__.py`
from .task_status_badge import set_badge_color

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
  . automappa.pages.home.tasks.task_status_badge.set_badge_color
  . automappa.tasks.aggregate_embeddings
  . automappa.tasks.count_kmer
  . automappa.tasks.embed_kmer
  . automappa.tasks.get_embedding_traces_df
  . automappa.tasks.normalize_kmer
  . automappa.tasks.preprocess_clusters_geom_medians
  . automappa.tasks.preprocess_marker_symbols
[2023-07-13 18:24:16,413: WARNING/MainProcess] /opt/conda/lib/python3.9/site-packages/celery/worker/consumer/consumer.py:498: CPendingDeprecationWarning: The broker_connection_retry configuration setting will no longer determine
whether broker connection retries are made during startup in Celery 6.0 and above.
If you wish to retain the existing behavior for retrying connections on startup,
you should set broker_connection_retry_on_startup to True.
  warnings.warn(
[2023-07-13 18:24:16,437: INFO/MainProcess] Connected to amqp://user:**@rabbitmq:5672//
[2023-07-13 18:24:16,439: WARNING/MainProcess] /opt/conda/lib/python3.9/site-packages/celery/worker/consumer/consumer.py:498: CPendingDeprecationWarning: The broker_connection_retry configuration setting will no longer determine
whether broker connection retries are made during startup in Celery 6.0 and above.
If you wish to retain the existing behavior for retrying connections on startup,
you should set broker_connection_retry_on_startup to True.
  warnings.warn(
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