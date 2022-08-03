# TODO (WIP)

1. [x] :art:::racehorse: Pass postgres datatable `table_name` back from `dash-uploader` callback
2. [x] :racehorse::art: `dcc.Store(...)` datatable id in `dcc.Store(...)`
3. [x] :racehorse::art: Save uploaded file metadata to postgres datatable
4. [x] :racehorse::art: Populate `dcc.Store(...)` with user's existing datatables
5. [ ] ~:racehorse::art: Populate `data_table.DataTable` with clickable `dcc.Link` that navigates user to `mag_refinement.py` (will load data relevant to link, e.g. metagenome annotations, markers, etc.)~
6. [x] :racehorse: Retrieve datatable within `mag_refinement.py`
    - [x] (`home.py`) binning, markers, metagenome dropdowns for selecting data available in database
    - [x] (`home.py`) dropdown values correspond to `table_id` and are sent to `mag_refinement.py` callbacks, replacing `pd.read_json(...)`
    - [x] (`home.py`/`index.py`) dropdowns should have a "NA" or placeholder disabling navigation to other layouts when data for the particular filetype is unavailable
7. [x] :art::bug: Finish addition of other embeddings within 2D scatterplot in `mag_refinement.py`
8. [x] :carrot::racehorse: Add celery task-queue
9. [x] :carrot::racehorse: Add celery-monitoring services
10. [ ] :carrot::racehorse: Add uploaded data ingestion to task-queue
11. [x] :carrot::racehorse: Add k-mer embedding tasks to task-queue
12. [x] :fire: Remove parser args for data inputs (i.e. not relevant to running automappa server)
13. [x] :art: Refactor `on_{binning,markers,metagenome}_upload` callbacks to one function that takes in the filetype to determine storage method
14. [x] :racehorse: Retrieve datatable within `mag_summary.py`
15. [x] :whale::elephant::sunflower: Grafana provision from within `docker-compose.yml`
16. [ ] :art::fire: Refactor `store_binning_main(...)` s.t. refinement-data is stored in a separate async process.
17. [ ] :art::carrot: Add selections/dropdowns/progress updates for metagenome embeddings
18. [x] :art: Add embeddings selection dropdown in settings for 2d scatterplot axes (place task queueing from these selections)
19. [ ] :art: Show some type of progress for metagenome ingestion to postgres DB
20. [x] :art: Dynamically Format scatterplot 2-d axes (i.e. Gc_Content to GC Content, etc.)
21. [ ] :racehorse: Reduce queries to postgres DB
22. [x] :bug::wrench: Fix scatterplot-2d.figure callback (LINENO#685) `ValueError: columns overlap but no suffix specified: Index(['5mers-ilr-umap_x_1', '5mers-ilr-umap_x_2'], dtype='object')`
23. [ ] :bug::wrench: Add `dcc.Interval`? or `interval` argument? to Scatterplot 2D Axes dropdown s.t. disabled is updated appropriately (poll availability of embeddings in pg DB)

--------------------------------------------------------------------------------------------------

## Misc. Resources

- [Dash Extensions Enrich Module](https://www.dash-extensions.com/getting-started/enrich)
- [docker-compose networking docs](<https://docs.docker.com/compose/networking/#links>)
- [live mongoDB dash example](<https://github.com/Coding-with-Adam/Dash-by-Plotly/blob/master/Dash_and_Databases/MongoDB/live-mongodb-dash.py>)
- [plotly dash `dcc.Store` docs](<https://dash.plotly.com/dash-core-components/store#store-clicks-example>)
- [dash bootstrap components docs](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/)
- [how to access rabbitmq publicly](<https://stackoverflow.com/questions/23020908/how-to-access-rabbitmq-publicly> "how to access RabbitMQ publicly")
- [StackOverflow: how to access rabbitmq publicly](https://stackoverflow.com/a/57612615 "StackOverflow: how to access RabbitMQ publicly")
