# TODO (WIP)

1. [x] :art:::racehorse: Pass postgres datatable `table_name` back from `dash-uploader` callback
2. [x] :racehorse::art: `dcc.Store(...)` datatable id in `dcc.Store(...)`
3. [x] :racehorse::art: Save uploaded file metadata to postgres datatable
4. [x] :racehorse::art: Populate `dcc.Store(...)` with user's existing datatables
5. [ ] ~:racehorse::art: Populate `data_table.DataTable` with clickable `dcc.Link` that navigates user to `mag_refinement.py` (will load data relevant to link, e.g. metagenome annotations, markers, etc.)~
6. [x] :racehorse: Retrieve datatable within `mag_refinement.py`
    - [x] binning, markers, metagenome dropdowns for selecting data available in database
    - [x] dropdown values correspond to `table_id` and are sent to `mag_refinement.py` callbacks, replacing `pd.read_json(...)`
    - [x] dropdowns should have a "NA" or placeholder causing inability to navigate to other layouts when data for the particular filetype is unavailable
7. [ ] :art::bug: Finish addition of other embeddings within 2D scatterplot in `mag_refinement.py`
8. [x] :carrot::racehorse: Add celery task-queue
9. [x] :carrot::racehorse: Add celery-monitoring services
10. [ ] :carrot::racehorse: Add uploaded data ingestion to task-queue
11. [ ] :carrot::racehorse: Add k-mer embedding tasks to task-queue
12. [x] :fire: Remove parser args for data inputs (i.e. not relevant to running automappa server)
13. [x] :art: Refactor `on_{binning,markers,metagenome}_upload` callbacks to one function that takes in the filetype to determine storage method
14. [ ] :racehorse: Retrieve datatable within `mag_summary.py`

--------------------------------------------------------------------------------------------------

## docker-compose services configuration

> NOTE: All of this assumes you have all docker services running via `make up` or `docker-compose up`

TODO: Provision grafana from `docker-compose.yml`. See: [Grafana provisioning example data source config file](https://grafana.com/docs/grafana/latest/administration/provisioning/#example-data-source-config-file)

## Monitoring Services

- flower link - [http://localhost:5555](http://localhost:5555)
- prometheus link - [http://localhost:9090](http://localhost:9090)
- grafana link - [http://localhost:3000](http://localhost:3000)

### Grafana configuration

- flower+prometheus+grafana [add prometheus as a data source in grafana](<https://flower.readthedocs.io/en/latest/prometheus-integration.html#add-prometheus-as-a-data-source-in-grafana> "flower+prometheus+grafana add prometheus as a data source in grafana")
- grafana link - [http://localhost:3000](http://localhost:3000)

Add the prometheus url as:

```bash
http://prometheus:9090
```

Notice the tutorial mentions `http://localhost:9090`, but since this is running as a service using `docker-compose` the hostname changes to the
`prometheus` alias (this is the name of the service in the `docker-compose.yml` file)

## Misc. Resources

- [docker-compose networking docs](<https://docs.docker.com/compose/networking/#links>)
- [live mongoDB dash example](<https://github.com/Coding-with-Adam/Dash-by-Plotly/blob/master/Dash_and_Databases/MongoDB/live-mongodb-dash.py>)
- [plotly dash `dcc.Store` docs](<https://dash.plotly.com/dash-core-components/store#store-clicks-example>)
- [dash bootstrap components docs](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/)
- [how to access rabbitmq publicly](<https://stackoverflow.com/questions/23020908/how-to-access-rabbitmq-publicly> "how to access RabbitMQ publicly")
- [StackOverflow: how to access rabbitmq publicly](https://stackoverflow.com/a/57612615 "StackOverflow: how to access RabbitMQ publicly")
