# TODO (WIP)

1. [x] :art:::racehorse: Pass postgres datatable `table_name` back from `dash-uploader` callback
2. [x] :racehorse::art: `dcc.Store(...)` datatable id in `dcc.Store(...)`
3. [ ] :racehorse::art: Populate `dcc.Store(...)` with user's existing datatables
4. [ ] :racehorse::art: Populate `data_table.DataTable` with clickable `dcc.Link` that navigates user to `mag_refinement.py` (will load data relevant to link, e.g. metagenome annotations, markers, etc.)
5. [ ] :racehorse: Retrieve datatable within `mag_refinement.py` and `mag_summary.py`
6. [ ] :art::bug: Finish addition of other embeddings within 2D scatterplot in `mag_refinement.py`
7. [ ] :carrot::racehorse: Add task-queue for ingesting uploaded data to postgres table
8. [ ] :carrot::racehorse: Add k-mer embedding tasks to task-queue
9. [x] :fire: Remove parser args for data inputs (i.e. not relevant to running automappa server)
