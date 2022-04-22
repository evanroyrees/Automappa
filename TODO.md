# TODO (WIP)

1. [x] :art:::racehorse: Pass postgres datatable `table_name` back from `dash-uploader` callback
2. [x] :racehorse::art: `dcc.Store(...)` datatable id in `dcc.Store(...)`
3. [x] :racehorse::art: Save uploaded file metadata to postgres datatable
4. [x] :racehorse::art: Populate `dcc.Store(...)` with user's existing datatables
5. [ ] :racehorse::art: Populate `data_table.DataTable` with clickable `dcc.Link` that navigates user to `mag_refinement.py` (will load data relevant to link, e.g. metagenome annotations, markers, etc.)
6. [ ] :racehorse: Retrieve datatable within `mag_refinement.py` and `mag_summary.py`
7. [ ] :art::bug: Finish addition of other embeddings within 2D scatterplot in `mag_refinement.py`
8. [ ] :carrot::racehorse: Add task-queue for ingesting uploaded data to postgres table
9. [ ] :carrot::racehorse: Add k-mer embedding tasks to task-queue
10. [x] :fire: Remove parser args for data inputs (i.e. not relevant to running automappa server)
11. [x] :art: Refactor `on_{binning,markers,metagenome}_upload` callbacks to one function that takes in the filetype to determine storage method

--------------------------------------------------------------------------------------------------

## Troubleshooting `docker-compose`

For some reason, when adding the `web` service in `docker-compose.yml`, postgres no
longer accepts connections. It emits the error:

```bash
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refused
 Is the server running on that host and accepting TCP/IP connections?
connection to server at "localhost" (::1), port 5432 failed: Cannot assign requested address
 Is the server running on that host and accepting TCP/IP connections?

(Background on this error at: https://sqlalche.me/e/14/e3q8)
```

IDEA: Maybe it has to do with the default driver or network? Upon generation (w/ the `web` service) it emits:

```bash
Creating network "automappa_default" with the default driver
```

> NOTE: When I comment out the `web` service and run only postgres _then_ run automappa in a separate
terminal, I am able to communicate with postgres and the tables are readily retrieved...

One possible solution to this could be explicitly specifying the URIs in the `docker-compose.yml`.
From inspecting a `docker-compose.yml` file from this repo (<https://github.com/felipeam86/fastapi-sqlmodel-dash/blob/main/docker-compose.yml>), it looks like this could allow passing the
appropriate URI based on the service...

When each service is constructed it is given its own `HOSTNAME` by docker.... However, it
automagically discovers the `DOCKER_IP` given to it by simply specifying the `service` _in place of_
the `HOSTNAME`.

## Misc. Resources

- [docker-compose networking docs](<https://docs.docker.com/compose/networking/#links>)
- [live mongoDB dash example](<https://github.com/Coding-with-Adam/Dash-by-Plotly/blob/master/Dash_and_Databases/MongoDB/live-mongodb-dash.py>)
- [plotly dash `dcc.Store` docs](<https://dash.plotly.com/dash-core-components/store#store-clicks-example>)
- [dash bootstrap components docs](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/)
