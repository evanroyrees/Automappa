# Contributing

## Index

- [Getting started](#getting-started-with-development)
  1. [Clone Automappa](#1-retrieve-repository)
  2. [Start Automappa services](#2-create-services-using-docker-compose)
  3. [Navigate to browser url](#3-navigate-to-the-automappa-page-in-your-browser)
- [Creating a component](#adding-a-new-component)
  
  0. [Before you begin](#0-before-your-begin)
  1. [Create `component-id` in `ids.py`](#1-create-a-unique-component-id)
  2. [Create component file](#2-create-your-componentpy-file)
  3. [Define a `render` function](#3-define-a-render-function)
  4. [Component interactions](#4-defining-component-interactions)
     - [The `app` argument](#the-app-argument)
     - [The `source` argument](#the-source-argument)
  5. [Add component to the page's layout](#5-import-and-render-your-component-into-the-page-layout)
  6. [Component `Input` to existing components](#6-using-your_component-as-an-input-to-existing-components)
- [Adding a page](#pages)
- [Services and dependencies](#automappa-services-and-dependencies)
  - [Postgres](#postgres)
  - [RabbitMQ](#rabbitmq)
  - [Celery](#celery-task-queue)
    - [task-queue docs](task-queue.md)
  - [Redis](#redis)
  - [Flower](#flower)
- [Dev Resources](#development-resources)
  - [Component libraries](#libraries)
  - [Monitoring services](#monitoring-and-task-queue-services)
- [🧭 roadmap](#roadmap)
  - [UI/UX enhancements](#uiux-enhancements)
  - [Pre-processing](#pre-processing)
  - [Post-processing](#post-processing)

## Getting started with development

### 1. Retrieve repository

```bash
git clone https://github.com/WiscEvan/Automappa.git
cd Automappa
```

### 2. Create services using `docker-compose`

For convenience, the command may be found in the `Makefile` and the services setup with:

```bash
make up
```

> NOTE: You can see a list of make commands by only tying `make` in the `Automappa` directory.

This may take a few minutes if all of the images need to be pulled and constructed.

### 3. Navigate to the Automappa page in your browser

After all of the images have been created the services will be started in their
respective containers and you should eventually see this in the terminal:

```console
automappa-web-1       | Dash is running on http://0.0.0.0:8050/
automappa-web-1       | 
automappa-web-1       | [INFO] dash.dash: Dash is running on http://0.0.0.0:8050/
automappa-web-1       | 
automappa-web-1       |  * Serving Flask app 'automappa.app'
automappa-web-1       |  * Debug mode: on
```

## Adding a new component

### 0. Before your begin

Checkout a new branch

```bash
git checkout -b <feature> develop
```

Change `SERVER_DEBUG = False` in `.env` to `SERVER_DEBUG = True`

### 1. Create a unique component id

A unique id is required to specify what data should be set or retrieved based on the component being implemented.

To do this, simply create a unique id for the component in `automappa/components/ids.py`

```python
# Example contents of automappa/components/ids.py
COMPONENT_ID = "unique-component-id"
```

This should ultimately be imported by the respective component's file (`automappa/pages/<page>/components/your_component.py`) like so:

```python
from automappa.components import ids
# Now you can access 'unique-component-id' with
ids.COMPONENT_ID
```

### 2. Create your `component.py` file

The component should be placed respective to the page where it will be added.

The name of the file should describe your component and be located in the `components` sub-directory.

i.e. `automappa/pages/<page>/components/your_component.py`

>NOTE: Try to be clear and concise when naming the component file

### 3. define a `render` function

Define a `render` function in `your_component.py`.

We'll start with:

```python
# contents of your_component.py
from dash_extensions.enrich import html

def render() -> html.Div:
    ...
```

All components follow a standard syntax of a `render` function.

### 4. Defining component interactions

#### The `app` argument

>Prior to this you should read about [Dash basic callbacks](<https://dash.plotly.com/basic-callbacks> "Dash callbacks documentation")
>
> and if the component behavior is more complex, you may also find
> the [Dash advanced callbacks docs](https://dash.plotly.com/advanced-callbacks "Dash advanced callbacks documentation")
> helpful.

To create a reactive component you will need to define a *callback function*
and describe the component's behavior when interacting with other components.

I'll provide a simple example here for registering callbacks specifically to your
component.

Remember, all components follow a standard syntax of a `render` function and
this takes as an argument the page's app (or `DashProxy`) as input arguments.

Here is a simple example with these arguments:

```python
# contents of your_component.py
from dash_extensions.enrich import html, DashProxy

def render(app: DashProxy) -> html.Div:
    ...
```

You'll notice the type hint is a `DashProxy` object. This is especially important
when defining callbacks specific to this component. We will need to register these
callbacks using the same `dash` basic callback syntax so we pass this in as input
to decouple the presenter (the `app`) from the component. This provides us two wonderful features.

1. We now have much greater flexibility
2. We can avoid having to put `from automappa.app import app` everywhere!

>This also reduces our chances of running in to problematic circular imports from
>having to pass the app around the entire codebase.

Let us proceed...

```python
# contents of your_component.py
from automappa.components import ids
from dash_extensions.enrich import html, DashProxy

def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.YOUR_COMPONENT_ID, "property"),
        Input(ids.A_COMPONENT_ID, "property"),
        ...
    )
    def callback_function(a_component_id_property):
        ...
```

The `app.callback(...)` can take any number of `Input`s and `Output`s.
Typically we'll only use one `Output` and may have multiple `Inputs` to have our
callback perform a specific task according to the user's interactions.

>NOTE: There are other keywords that may be supplied to `@app.callback` and you can
find more information on this in the
[Dash basic callbacks docs](<https://dash.plotly.com/basic-callbacks> "Dash callbacks documentation")
and [Dash advanced callbacks docs](https://dash.plotly.com/advanced-callbacks "Dash advanced callbacks documentation").

The `callback_function` to create a reactive component in the app may have an
arbitrary name but I tend to stick with something related to the type of
reactivity of the component and what property is being updated.

You will have to check your particular component's documentation to determine
the properties that are available (often referred to as `props`).

```python
from automappa.components import ids
from dash_extensions.enrich import DashProxy,html,dcc


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.COMPONENT_ID, "<component-property>"),
        Input(ids.<some_input_component_id>, "<component-property>"),
    )
    def your_component_callback(some_input_component_prop):
        ...
        return ...
    ...
    return html.Div(dcc.Component(id=ids.COMPONENT_ID, ...), ...)
```

>NOTE: The actual `app` object that will ultimately be passed to this is
 a `DashBlueprint` which is a wrapper of `DashProxy` used similarly to flask
blueprint templates. For more details on this see the respective
`automappa/pages/<page>/layout.py` file.

#### The `source` argument

Up until now we've only discussed the `app: DashProxy` argument in
`def render(...)`, but we still require one more argument--a "data source".
We will use this to access uploaded user data.

The database setup has been isolated to its own directory under:
`automappa/data/{database,models,schemas,loader}.py`

The respective data source will use these database objects for the respective page.

All of the Automappa pages have their own data source.

For example if we look at the `mag_refinement` page, we will notice three items:

a `components` directory containing the page's components and two files, `layout.py` and `source.py`

The components and data source are implemented, then imported in 
`layout.py` to be instantiated in the page's layout (i.e. in a `render` function)

```bash
automappa/pages/mag_refinement
├── __init__.py
├── components
├── layout.py
├── source.py
└── tests

2 directories, 3 files
```

The data source handles all of the component methods used to interact with the database.

Here we outline our database, models (w/schemas), loading and pre-processing
methods to construct a `DataSource` object that can handle any database operations.
Furthermore datasources may be defined for each page allowing us to avoid one.
"god" class that requires all data operations for all pages and components

>(What a headache that would be 🤮)

At startup, Automappa will create multiple sources respective to each page, e.g: a `HomeDataSource`, `RefinementDataSource` and `SummaryDataSource`.

> (I've left `MAG` from the MAG-summary and MAG-refinement page
>names b/c I don't think they look so nice in CamelCase)

Instead of running in to a similar problem to `from automappa.app import app` we
can decouple our data source from our components by *dependency inversion*.

We do this by defining our component's data source *protocol* to ensure we have
all of the methods available in our data source that are required by the component.

For a simple example, let's say our component needs to retrieve the number of contigs
within a GC% range. We can define the data source protocol with the necessary method
to use in our component.

We will need to add a `ComponentDataSource` protocol to access the user's `Contig` data.

>NOTE: For more information on the `Contig` model see: `automappa/data/models.py`

```python
# contents of automappa/pages/mag_refinement/components/your_component.py
from typing import Protocol,Tuple

class ComponentDataSource(Protocol):
    def get_contig_count_in_gc_content_range(self, min_max_values: Tuple[float,float]) -> int:
        ...
```

This allows the python typing system to detect when this method is available while
the provided data source is being used. Notice the arguments and the returned
object are typehinted to tell the editor the protocol behavior.

Now let's see this in action with a fake example broken into bitesize pieces:

```python
# contents of automappa/pages/mag_refinement/components/your_component.py
from dash_extenesions.enrich import DashProxy,html
from typing import Protocol,Tuple

class ComponentDataSource(Protocol):
    def get_contig_count_in_gc_content_range(self, min_max_values: Tuple[float,float]) -> int:
        ...

def render(app: DashProxy, source: ComponentDataSource) -> html.Div:
    # More code below
```

Here we provide our source type using our protocol: `source: ComponentDataSource` and this allows us
to continue on with the component's implementation without any data source imports! 🤯

Let's continue with using the `source` in a callback...

> NOTE: I've also added typehints to the callback function below (this was omitted in
>previous examples for simplicity, but should always be done 🙈).

```python
# contents of automappa/pages/mag_refinement/components/your_component.py
from dash_extenesions.enrich import DashProxy,html
import dash_mantine_components as dmc
from typing import Protocol,Tuple

class ComponentDataSource(Protocol):
    def get_contig_count_in_gc_content_range(self, min_max_values: Tuple[float,float]) -> int:
        ...

def render(app: DashProxy, source: ComponentDataSource) -> html.Div:
    @app.callback(
        Output(ids.COMPONENT_ID, "children"),
        Input(ids.GC_CONTENT_RANGE_SLIDER, "value"),
    )
    def show_contig_count_in_range(gc_content_range: Tuple[float,float]) -> dmc.Text:
        # we use our data source object here to get our count in the component
        contig_count = source.get_contig_count_in_gc_content_range(
            min_max_values=gc_content_range
        )
        return dmc.Text(f"{contig_count=}")
```

Notice we can use our `source.get_contig_count_in_gc_content_range` method
(Possibly without it yet being implemented) in the callback behavior. Of course,
once all of this is in place, you will need to make sure the actual passed
`source` object has this method implemented.

>NOTE: You should be able to find the passed `source` object's type by looking
at the respective layout file:
>
>i.e. `automappa/pages/mag_refinement/components/your_component.py` is placed in
>`automappa/pages/mag_refinement/layout.py` which gets passed a `RefinementDataSource`
>in `automappa/components/layout.py`

#### The data source graph

The passing of the data source objects may be visualized in the following graph

Here is an overview of all of the data sources

>NOTE: The square rectangles contain the implemented database operations
> while the rounded rectangles depict protocol classes to define component behavior.

```mermaid
graph TD;
    subgraph MAG-summary Page
    A[SummaryDataSource]-->B(SummaryLayoutDataSource);
    B(SummaryLayoutDataSource)-->C(CoverageOverviewBoxplotDataSource);
    B(SummaryLayoutDataSource)-->D(GcPercentOverviewBoxplotDataSource);
    B(SummaryLayoutDataSource)-->E(LengthOverviewBoxplotDataSource);
    B(SummaryLayoutDataSource)-->F(ClusterMetricsBoxplotDataSource);
    B(SummaryLayoutDataSource)-->G(ClusterDropdownDataSource);
    B(SummaryLayoutDataSource)-->H(ClusterStatsTableDataSource);
    B(SummaryLayoutDataSource)-->I(ClusterTaxonomyDistributionDataSource);
    B(SummaryLayoutDataSource)-->J(ClusterMetricsBarplotDataSource);
    end
    subgraph MAG-refinement Page
    AA[RefinementDataSource]-->BB(RefinementLayoutDataSource);
    BB(RefinementLayoutDataSource)-->CC(Scatterplot2dDataSource);
    BB(RefinementLayoutDataSource)-->DD(SettingsOffcanvasDataSource);
    BB(RefinementLayoutDataSource)-->EE(MagMetricsDataSource);
    BB(RefinementLayoutDataSource)-->FF(TaxonomyDistributionDataSource);
    BB(RefinementLayoutDataSource)-->GG(Scatterplot3dDataSource);
    BB(RefinementLayoutDataSource)-->HH(CoverageBoxplotDataSource);
    BB(RefinementLayoutDataSource)-->II(GcPercentBoxplotDataSource);
    BB(RefinementLayoutDataSource)-->JJ(LengthBoxplotDataSource);
    BB(RefinementLayoutDataSource)-->KK(ContigCytoscapeDataSource);
    BB(RefinementLayoutDataSource)-->LL(CoverageRangeSliderDataSource);
    end
    subgraph Home Page
    AAA[HomeDataSource]-->BBB(HomeLayoutDataSource);
    BBB(HomeLayoutDataSource)-->CCC(UploadModalButtonDataSource);
    BBB(HomeLayoutDataSource)-->DDD(SampleCardsDataSource);
    end
```

<details>

<summary>Home page data source graph</summary>

```mermaid
graph TD;
    A[HomeDataSource]-->B(HomeLayoutDataSource);
    B(HomeLayoutDataSource)-->C(UploadModalButtonDataSource);
    B(HomeLayoutDataSource)-->D(SampleCardsDataSource);
```

</details>

<details>

<summary>MAG-refinement data source graph</summary>

```mermaid
graph TD;
    A[RefinementDataSource]-->B(RefinementLayoutDataSource);
    B(RefinementLayoutDataSource)-->C(Scatterplot2dDataSource);
    B(RefinementLayoutDataSource)-->D(SettingsOffcanvasDataSource);
    B(RefinementLayoutDataSource)-->E(MagMetricsDataSource);
    B(RefinementLayoutDataSource)-->F(TaxonomyDistributionDataSource);
    B(RefinementLayoutDataSource)-->G(Scatterplot3dDataSource);
    B(RefinementLayoutDataSource)-->H(CoverageBoxplotDataSource);
    B(RefinementLayoutDataSource)-->I(GcPercentBoxplotDataSource);
    B(RefinementLayoutDataSource)-->J(LengthBoxplotDataSource);
    B(RefinementLayoutDataSource)-->K(ContigCytoscapeDataSource);
    B(RefinementLayoutDataSource)-->L(CoverageRangeSliderDataSource);
```

</details>

<details>

<summary>MAG-summary data source graph</summary>

```mermaid
graph TD;
    A[SummaryDataSource]-->B(SummaryLayoutDataSource);
    B(SummaryLayoutDataSource)-->C(CoverageOverviewBoxplotDataSource);
    B(SummaryLayoutDataSource)-->D(GcPercentOverviewBoxplotDataSource);
    B(SummaryLayoutDataSource)-->E(LengthOverviewBoxplotDataSource);
    B(SummaryLayoutDataSource)-->F(ClusterMetricsBoxplotDataSource);
    B(SummaryLayoutDataSource)-->G(ClusterDropdownDataSource);
    B(SummaryLayoutDataSource)-->H(ClusterStatsTableDataSource);
    B(SummaryLayoutDataSource)-->I(ClusterTaxonomyDistributionDataSource);
    B(SummaryLayoutDataSource)-->J(ClusterMetricsBarplotDataSource);
```

</details>

A placeholder definition may be made within the passed `source` objects
class while working out the component's behavior and interactions.
This makes the required method easier to find when returning to the
data handling aspect of the implementation.

For example, we know we want a `get_contig_count_in_gc_content_range` method and because
we are placing our component in the MAG-refinement layout can we define this in
`RefinementDataSource`.

>i.e. `RefinementDataSource` is the object that will ultimately
>be passed to `your_component.render(app, source)`.

```python
# contents of automappa/pages/mag_refinement/source.py
class RefinementDataSource(BaseModel):
    def get_contig_count_in_gc_content_range(self, min_max_values: Tuple[float,float]) -> int:
        raise NotImplemented
```

Let's say we've finalized our component behavior and aesthetics.

Here's the final fake example component in its entirety:

```python
# contents of automappa/pages/mag_refinement/components/your_component.py
from dash_extenesions.enrich import DashProxy,html
import dash_mantine_components as dmc
from typing import Protocol,Tuple

class ComponentDataSource(Protocol):
    def get_contig_count_in_gc_content_range(self, min_max_values: Tuple[float,float]) -> int:
        ...

def render(app: DashProxy, source: ComponentDataSource) -> html.Div:
    @app.callback(
        Output(ids.COMPONENT_ID, "children"),
        Input(ids.GC_CONTENT_RANGE_SLIDER, "value"),
    )
    def show_contig_count_in_range(gc_content_range: Tuple[float,float]) -> dmc.Text:
        contig_count = source.get_contig_count_in_gc_content_range(
            min_max_values=gc_content_range
        )
        return dmc.Text(f"{contig_count=}")
    
    return html.Div(ids.COMPONENT_ID,
        children = [
            """
            Interact with the GC% slider to see how many contigs are within the
            selected range.
            """
        ]
    )
```

We can now return to the data source and should not need to make any further changes with the
component:

Returning to our data source implementation...

```python
# contents of automappa/pages/mag_refinement/source.py
class RefinementDataSource(BaseModel):
    def get_contig_count_in_gc_content_range(self, min_max_values: Tuple[float,float]) -> int:
        raise NotImplemented
```

...we implement the required database query operation

```python
# contents of automappa/pages/mag_refinement/source.py
class RefinementDataSource(BaseModel):
    def get_contig_count_in_gc_content_range(self, min_max_values: Tuple[float,float]) -> int:
        min_gc_content, max_gc_content = min_max_values
        with Session(engine) as session:
            statement = (
                select(Contig) # Here we use the Contig model defined in models.py
                .where(Contig.gc_content >= min_gc_content, Contig.gc_content <= max_gc_content)
            )
            results = session.exec(statement).all()
        return len(results)
```

### 5. Import and render your component into the page layout

At this point, the majority of the work has been done, now all that is left is to simply place the component
into the layout of the page. This should correspond to the same page for which the component is implemented

- `automappa/pages/<page>/layout.py`

Following the example above, this would be `automappa/pages/mag_refinement/layout.py`

```python
# contents of automappa/pages/mag_refinement/layout.py
from dash_extenesions.enrich import DashProxy,html
from automappa.pages.mag_refinement.components import your_component # importing your component
from typing import Protocol

class RefinementLayoutDataSource(Protocol):
    ...
    def get_contig_count_in_gc_content_range(self, min_max_values: Tuple[float,float]) -> int:
        ...

def render(app: DashProxy, source: RefinementLayoutDataSource) -> html.Div:
    # ... code above this
    
    # Including the component within the page layout
    app.layout = html.Div(your_component.render(app, source))
    
    return app
```

### 6. Using `your_component` as an input to existing components

To retrieve information from components while interacting with the application
`dash` uses the `@app.callback(Output, Input)` syntax as we have seen.

>NOTE: There are other keywords that may be supplied to `@app.callback` and you can
find more information on this in the [Dash basic callbacks docs](<<https://dash.plotly.com/basic-callbacks> "Dash callbacks documentation") and [Dash advanced callbacks docs](https://dash.plotly.com/advanced-callbacks "Dash advanced callbacks documentation").

###### [Back to top](#contributing)

## Pages

> If you are not adding a page to Automappa but simply a component to an existing page, you may skip this section.

Automappa uses a dash feature called [`pages`](https://dash.plotly.com/urls "dash pages documentation") to allow multi-page navigation
*without* having to explicitly define callbacks for rendering each page (more on this later).

Similarly, many useful dash utilities are also available in a package called
[`dash-extensions`](https://www.dash-extensions.com/ "dash extensions documentation")
which has been used throughout. Unfortunately these packages are not completely synchronized,
so the simple approach as described in the dash documentation may not be taken. However, some workarounds
are described in the [dash-extensions docs](https://www.dash-extensions.com/getting_started/enrich).

###### [Back to top](#contributing)

## Automappa services and dependencies

Currently Automappa utilizes multiple services to manage its backend database,
task-queue and monitoring. You may find additional details on these services with
their respective docker image builds, Dockerfiles, commands, dependencies and their
ports in the `docker-compose.yml` file.

These services are:

| Service | Purpose | Description |
| -: | :- | :- |
| `postgres` | sample DB | backend database to store/retrieve user uploaded data |
| `rabbitmq` | task-queue broker | task-queue broker for managing worker tasks |
| `celery` | task-queue worker | task-queue worker |
| `redis` | task-queue DB |  task-queue broker & worker backend for passing tasks to/from the task-queue |
| `flower` | task-queue monitor | for monitoring `celery` and `rabbitmq` task-queue |
| `web` | App | The automappa web instance |
| \(Not currently in use\) `prometheus` | service monitoring | service monitoring dashboard |
| \(Not currently in use\) `grafana` | service monitoring | service monitoring dashboard |

Customization of the urls to these services may be
performed by editing the `.env` files as many of
these settings are configured from here.

###### [Back to top](#contributing)

### Postgres

<details>

<summary>What to see at startup</summary>

```console
The files belonging to this database system will be owned by user "postgres".
This user must also own the server process.
The database cluster will be initialized with locale "en_US.utf8".
The default database encoding has accordingly been set to "UTF8".
The default text search configuration will be set to "english".
Data page checksums are disabled.
fixing permissions on existing directory /var/lib/postgresql/data ... ok
creating subdirectories ... ok
selecting dynamic shared memory implementation ... posix
selecting default max_connections ... 100
selecting default shared_buffers ... 128MB
selecting default time zone ... Etc/UTC
creating configuration files ... ok
running bootstrap script ... ok
performing post-bootstrap initialization ... ok
syncing data to disk ... ok
Success. You can now start the database server using:
    pg_ctl -D /var/lib/postgresql/data -l logfile start
initdb: warning: enabling "trust" authentication for local connections
initdb: hint: You can change this by editing pg_hba.conf or using the option -A, or --auth-local and --auth-host, the next time you run initdb.
waiting for server to start....2023-06-30 16:28:09.344 UTC [49] LOG:  starting PostgreSQL 15.3 (Debian 15.3-1.pgdg110+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 10.2.1-6) 10.2.1 20210110, 64-bit
2023-06-30 16:28:09.348 UTC [49] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
2023-06-30 16:28:09.404 UTC [52] LOG:  database system was shut down at 2023-06-30 16:28:08 UTC
2023-06-30 16:28:09.436 UTC [49] LOG:  database system is ready to accept connections
 done
server started
CREATE DATABASE
/usr/local/bin/docker-entrypoint.sh: ignoring /docker-entrypoint-initdb.d/*
waiting for server to shut down....2023-06-30 16:28:09.728 UTC [49] LOG:  received fast shutdown request
2023-06-30 16:28:09.737 UTC [49] LOG:  aborting any active transactions
2023-06-30 16:28:09.742 UTC [49] LOG:  background worker "logical replication launcher" (PID 55) exited with exit code 1
2023-06-30 16:28:09.742 UTC [50] LOG:  shutting down
2023-06-30 16:28:09.744 UTC [50] LOG:  checkpoint starting: shutdown immediate
2023-06-30 16:28:09.845 UTC [50] LOG:  checkpoint complete: wrote 918 buffers (5.6%); 0 WAL file(s) added, 0 removed, 0 recycled; write=0.044 s, sync=0.048 s, total=0.103 s; sync files=250, longest=0.017 s, average=0.001 s; distance=4217 kB, estimate=4217 kB
2023-06-30 16:28:09.857 UTC [49] LOG:  database system is shut down
 done
server stopped
PostgreSQL init process complete; ready for start up.
2023-06-30 16:28:10.158 UTC [1] LOG:  starting PostgreSQL 15.3 (Debian 15.3-1.pgdg110+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 10.2.1-6) 10.2.1 20210110, 64-bit
2023-06-30 16:28:10.159 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
2023-06-30 16:28:10.159 UTC [1] LOG:  listening on IPv6 address "::", port 5432
2023-06-30 16:28:10.234 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
2023-06-30 16:28:10.264 UTC [65] LOG:  database system was shut down at 2023-06-30 16:28:09 UTC
2023-06-30 16:28:10.317 UTC [1] LOG:  database system is ready to accept connections
```

</details>

###### [Back to top](#contributing)

### RabbitMQ

<details>

<summary>What to see at startup</summary>

```console
2023-06-30 17:34:00.261066+00:00 [info] <0.221.0> Feature flags: list of feature flags found:
2023-06-30 17:34:00.283893+00:00 [info] <0.221.0> Feature flags:   [ ] classic_mirrored_queue_version
2023-06-30 17:34:00.284137+00:00 [info] <0.221.0> Feature flags:   [ ] implicit_default_bindings
2023-06-30 17:34:00.284185+00:00 [info] <0.221.0> Feature flags:   [ ] maintenance_mode_status
2023-06-30 17:34:00.284446+00:00 [info] <0.221.0> Feature flags:   [ ] quorum_queue
2023-06-30 17:34:00.284501+00:00 [info] <0.221.0> Feature flags:   [ ] stream_queue
2023-06-30 17:34:00.284579+00:00 [info] <0.221.0> Feature flags:   [ ] user_limits
2023-06-30 17:34:00.284604+00:00 [info] <0.221.0> Feature flags:   [ ] virtual_host_metadata
2023-06-30 17:34:00.284852+00:00 [info] <0.221.0> Feature flags: feature flag states written to disk: yes
2023-06-30 17:34:01.106535+00:00 [noti] <0.44.0> Application syslog exited with reason: stopped
2023-06-30 17:34:01.106765+00:00 [noti] <0.221.0> Logging: switching to configured handler(s); following messages may not be visible in this log output
2023-06-30 17:34:01.148394+00:00 [notice] <0.221.0> Logging: configured log handlers are now ACTIVE
2023-06-30 17:34:03.546573+00:00 [info] <0.221.0> ra: starting system quorum_queues
2023-06-30 17:34:03.546895+00:00 [info] <0.221.0> starting Ra system: quorum_queues in directory: /var/lib/rabbitmq/mnesia/rabbit@2b6eb27dd567/quorum/rabbit@2b6eb27dd567
2023-06-30 17:34:03.748480+00:00 [info] <0.259.0> ra system 'quorum_queues' running pre init for 0 registered servers
2023-06-30 17:34:03.805062+00:00 [info] <0.260.0> ra: meta data store initialised for system quorum_queues. 0 record(s) recovered
2023-06-30 17:34:03.831474+00:00 [notice] <0.265.0> WAL: ra_log_wal init, open tbls: ra_log_open_mem_tables, closed tbls: ra_log_closed_mem_tables
2023-06-30 17:34:03.905788+00:00 [info] <0.221.0> ra: starting system coordination
2023-06-30 17:34:03.905986+00:00 [info] <0.221.0> starting Ra system: coordination in directory: /var/lib/rabbitmq/mnesia/rabbit@2b6eb27dd567/coordination/rabbit@2b6eb27dd567
2023-06-30 17:34:03.964700+00:00 [info] <0.272.0> ra system 'coordination' running pre init for 0 registered servers
2023-06-30 17:34:03.985701+00:00 [info] <0.273.0> ra: meta data store initialised for system coordination. 0 record(s) recovered
2023-06-30 17:34:03.986268+00:00 [notice] <0.278.0> WAL: ra_coordination_log_wal init, open tbls: ra_coordination_log_open_mem_tables, closed tbls: ra_coordination_log_closed_mem_tables
2023-06-30 17:34:03.995172+00:00 [info] <0.221.0> 
2023-06-30 17:34:03.995172+00:00 [info] <0.221.0>  Starting RabbitMQ 3.10.1 on Erlang 24.3.4 [jit]
2023-06-30 17:34:03.995172+00:00 [info] <0.221.0>  Copyright (c) 2007-2022 VMware, Inc. or its affiliates.
2023-06-30 17:34:03.995172+00:00 [info] <0.221.0>  Licensed under the MPL 2.0. Website: https://rabbitmq.com
  ##  ##      RabbitMQ 3.10.1
  ##  ##
  ##########  Copyright (c) 2007-2022 VMware, Inc. or its affiliates.
  ######  ##
  ##########  Licensed under the MPL 2.0. Website: https://rabbitmq.com
  Erlang:      24.3.4 [jit]
  TLS Library: OpenSSL - OpenSSL 1.1.1o  3 May 2022
  Doc guides:  https://rabbitmq.com/documentation.html
  Support:     https://rabbitmq.com/contact.html
  Tutorials:   https://rabbitmq.com/getstarted.html
  Monitoring:  https://rabbitmq.com/monitoring.html
  Logs: /var/log/rabbitmq/rabbit@2b6eb27dd567_upgrade.log
        <stdout>
  Config file(s): /etc/rabbitmq/rabbitmq.conf
                  /etc/rabbitmq/conf.d/10-defaults.conf
  Starting broker...2023-06-30 17:34:04.002324+00:00 [info] <0.221.0> 
2023-06-30 17:34:04.002324+00:00 [info] <0.221.0>  node           : rabbit@2b6eb27dd567
2023-06-30 17:34:04.002324+00:00 [info] <0.221.0>  home dir       : /var/lib/rabbitmq
2023-06-30 17:34:04.002324+00:00 [info] <0.221.0>  config file(s) : /etc/rabbitmq/rabbitmq.conf
2023-06-30 17:34:04.002324+00:00 [info] <0.221.0>                 : /etc/rabbitmq/conf.d/10-defaults.conf
2023-06-30 17:34:04.002324+00:00 [info] <0.221.0>  cookie hash    : 8HBUegOS1ZYW39ARQeqjQw==
2023-06-30 17:34:04.002324+00:00 [info] <0.221.0>  log(s)         : /var/log/rabbitmq/rabbit@2b6eb27dd567_upgrade.log
2023-06-30 17:34:04.002324+00:00 [info] <0.221.0>                 : <stdout>
2023-06-30 17:34:04.002324+00:00 [info] <0.221.0>  database dir   : /var/lib/rabbitmq/mnesia/rabbit@2b6eb27dd567
2023-06-30 17:34:05.276918+00:00 [info] <0.221.0> Feature flags: list of feature flags found:
2023-06-30 17:34:05.277003+00:00 [info] <0.221.0> Feature flags:   [ ] classic_mirrored_queue_version
2023-06-30 17:34:05.277036+00:00 [info] <0.221.0> Feature flags:   [ ] drop_unroutable_metric
2023-06-30 17:34:05.277062+00:00 [info] <0.221.0> Feature flags:   [ ] empty_basic_get_metric
2023-06-30 17:34:05.277174+00:00 [info] <0.221.0> Feature flags:   [ ] implicit_default_bindings
2023-06-30 17:34:05.277205+00:00 [info] <0.221.0> Feature flags:   [ ] maintenance_mode_status
2023-06-30 17:34:05.277256+00:00 [info] <0.221.0> Feature flags:   [ ] quorum_queue
2023-06-30 17:34:05.277362+00:00 [info] <0.221.0> Feature flags:   [ ] stream_queue
2023-06-30 17:34:05.277392+00:00 [info] <0.221.0> Feature flags:   [ ] user_limits
2023-06-30 17:34:05.277414+00:00 [info] <0.221.0> Feature flags:   [ ] virtual_host_metadata
2023-06-30 17:34:05.277436+00:00 [info] <0.221.0> Feature flags: feature flag states written to disk: yes
2023-06-30 17:34:15.876746+00:00 [info] <0.221.0> Running boot step pre_boot defined by app rabbit
2023-06-30 17:34:15.876861+00:00 [info] <0.221.0> Running boot step rabbit_global_counters defined by app rabbit
2023-06-30 17:34:15.877406+00:00 [info] <0.221.0> Running boot step rabbit_osiris_metrics defined by app rabbit
2023-06-30 17:34:15.878840+00:00 [info] <0.221.0> Running boot step rabbit_core_metrics defined by app rabbit
2023-06-30 17:34:15.884054+00:00 [info] <0.221.0> Running boot step rabbit_alarm defined by app rabbit
2023-06-30 17:34:15.903243+00:00 [info] <0.293.0> Memory high watermark set to 3183 MiB (3338434969 bytes) of 7959 MiB (8346087424 bytes) total
2023-06-30 17:34:15.925580+00:00 [info] <0.295.0> Enabling free disk space monitoring
2023-06-30 17:34:15.926199+00:00 [info] <0.295.0> Disk free limit set to 50MB
2023-06-30 17:34:15.939181+00:00 [info] <0.221.0> Running boot step code_server_cache defined by app rabbit
2023-06-30 17:34:15.939630+00:00 [info] <0.221.0> Running boot step file_handle_cache defined by app rabbit
2023-06-30 17:34:15.940030+00:00 [info] <0.300.0> Limiting to approx 1048479 file handles (943629 sockets)
2023-06-30 17:34:15.940233+00:00 [info] <0.301.0> FHC read buffering: OFF
2023-06-30 17:34:15.940415+00:00 [info] <0.301.0> FHC write buffering: ON
2023-06-30 17:34:15.951372+00:00 [info] <0.221.0> Running boot step worker_pool defined by app rabbit
2023-06-30 17:34:15.963058+00:00 [info] <0.280.0> Will use 4 processes for default worker pool
2023-06-30 17:34:15.963293+00:00 [info] <0.280.0> Starting worker pool 'worker_pool' with 4 processes in it
2023-06-30 17:34:15.967054+00:00 [info] <0.221.0> Running boot step database defined by app rabbit
2023-06-30 17:34:15.969249+00:00 [info] <0.221.0> Node database directory at /var/lib/rabbitmq/mnesia/rabbit@2b6eb27dd567 is empty. Assuming we need to join an existing cluster or initialise from scratch...
2023-06-30 17:34:15.969382+00:00 [info] <0.221.0> Configured peer discovery backend: rabbit_peer_discovery_classic_config
2023-06-30 17:34:15.969952+00:00 [info] <0.221.0> Will try to lock with peer discovery backend rabbit_peer_discovery_classic_config
2023-06-30 17:34:15.970220+00:00 [info] <0.221.0> All discovered existing cluster peers:
2023-06-30 17:34:15.970294+00:00 [info] <0.221.0> Discovered no peer nodes to cluster with. Some discovery backends can filter nodes out based on a readiness criteria. Enabling debug logging might help troubleshoot.
2023-06-30 17:34:15.987668+00:00 [notice] <0.44.0> Application mnesia exited with reason: stopped
2023-06-30 17:34:17.120283+00:00 [info] <0.221.0> Waiting for Mnesia tables for 30000 ms, 9 retries left
2023-06-30 17:34:17.120457+00:00 [info] <0.221.0> Successfully synced tables from a peer
2023-06-30 17:34:17.227311+00:00 [info] <0.221.0> Waiting for Mnesia tables for 30000 ms, 9 retries left
2023-06-30 17:34:17.228954+00:00 [info] <0.221.0> Successfully synced tables from a peer
2023-06-30 17:34:17.229093+00:00 [info] <0.221.0> Feature flag `classic_mirrored_queue_version`: supported, attempt to enable...
2023-06-30 17:34:17.229312+00:00 [info] <0.221.0> Feature flag `classic_mirrored_queue_version`: mark as enabled=state_changing
2023-06-30 17:34:17.247984+00:00 [info] <0.221.0> Feature flags: list of feature flags found:
2023-06-30 17:34:17.248114+00:00 [info] <0.221.0> Feature flags:   [~] classic_mirrored_queue_version
2023-06-30 17:34:17.248175+00:00 [info] <0.221.0> Feature flags:   [ ] drop_unroutable_metric
2023-06-30 17:34:17.248316+00:00 [info] <0.221.0> Feature flags:   [ ] empty_basic_get_metric
2023-06-30 17:34:17.248362+00:00 [info] <0.221.0> Feature flags:   [ ] implicit_default_bindings
2023-06-30 17:34:17.248402+00:00 [info] <0.221.0> Feature flags:   [ ] maintenance_mode_status
2023-06-30 17:34:17.249184+00:00 [info] <0.221.0> Feature flags:   [ ] quorum_queue
2023-06-30 17:34:17.249280+00:00 [info] <0.221.0> Feature flags:   [ ] stream_queue
2023-06-30 17:34:17.249326+00:00 [info] <0.221.0> Feature flags:   [ ] user_limits
2023-06-30 17:34:17.249362+00:00 [info] <0.221.0> Feature flags:   [ ] virtual_host_metadata
2023-06-30 17:34:17.249757+00:00 [info] <0.221.0> Feature flags: feature flag states written to disk: yes
2023-06-30 17:34:17.366149+00:00 [info] <0.221.0> Feature flag `classic_mirrored_queue_version`: mark as enabled=true
2023-06-30 17:34:17.371476+00:00 [info] <0.221.0> Feature flags: list of feature flags found:
2023-06-30 17:34:17.372173+00:00 [info] <0.221.0> Feature flags:   [x] classic_mirrored_queue_version
2023-06-30 17:34:17.373462+00:00 [info] <0.221.0> Feature flags:   [ ] drop_unroutable_metric
2023-06-30 17:34:17.373578+00:00 [info] <0.221.0> Feature flags:   [ ] empty_basic_get_metric
2023-06-30 17:34:17.373652+00:00 [info] <0.221.0> Feature flags:   [ ] implicit_default_bindings
2023-06-30 17:34:17.376918+00:00 [info] <0.221.0> Feature flags:   [ ] maintenance_mode_status
2023-06-30 17:34:17.377137+00:00 [info] <0.221.0> Feature flags:   [ ] quorum_queue
2023-06-30 17:34:17.377231+00:00 [info] <0.221.0> Feature flags:   [ ] stream_queue
2023-06-30 17:34:17.377740+00:00 [info] <0.221.0> Feature flags:   [ ] user_limits
2023-06-30 17:34:17.377890+00:00 [info] <0.221.0> Feature flags:   [ ] virtual_host_metadata
2023-06-30 17:34:17.378438+00:00 [info] <0.221.0> Feature flags: feature flag states written to disk: yes
2023-06-30 17:34:17.467765+00:00 [info] <0.221.0> Feature flag `drop_unroutable_metric`: supported, attempt to enable...
2023-06-30 17:34:17.467873+00:00 [info] <0.221.0> Feature flag `drop_unroutable_metric`: mark as enabled=state_changing
2023-06-30 17:34:17.470253+00:00 [info] <0.221.0> Feature flags: list of feature flags found:
2023-06-30 17:34:17.470443+00:00 [info] <0.221.0> Feature flags:   [x] classic_mirrored_queue_version
2023-06-30 17:34:17.470530+00:00 [info] <0.221.0> Feature flags:   [~] drop_unroutable_metric
2023-06-30 17:34:17.470602+00:00 [info] <0.221.0> Feature flags:   [ ] empty_basic_get_metric
2023-06-30 17:34:17.470699+00:00 [info] <0.221.0> Feature flags:   [ ] implicit_default_bindings
2023-06-30 17:34:17.470794+00:00 [info] <0.221.0> Feature flags:   [ ] maintenance_mode_status
2023-06-30 17:34:17.470853+00:00 [info] <0.221.0> Feature flags:   [ ] quorum_queue
2023-06-30 17:34:17.470908+00:00 [info] <0.221.0> Feature flags:   [ ] stream_queue
2023-06-30 17:34:17.470969+00:00 [info] <0.221.0> Feature flags:   [ ] user_limits
2023-06-30 17:34:17.471009+00:00 [info] <0.221.0> Feature flags:   [ ] virtual_host_metadata
2023-06-30 17:34:17.471050+00:00 [info] <0.221.0> Feature flags: feature flag states written to disk: yes
2023-06-30 17:34:17.578161+00:00 [info] <0.221.0> Feature flag `drop_unroutable_metric`: mark as enabled=true
2023-06-30 17:34:17.586106+00:00 [info] <0.221.0> Feature flags: list of feature flags found:
2023-06-30 17:34:17.586306+00:00 [info] <0.221.0> Feature flags:   [x] classic_mirrored_queue_version
2023-06-30 17:34:17.586371+00:00 [info] <0.221.0> Feature flags:   [x] drop_unroutable_metric
2023-06-30 17:34:17.586414+00:00 [info] <0.221.0> Feature flags:   [ ] empty_basic_get_metric
2023-06-30 17:34:17.586466+00:00 [info] <0.221.0> Feature flags:   [ ] implicit_default_bindings
2023-06-30 17:34:17.586505+00:00 [info] <0.221.0> Feature flags:   [ ] maintenance_mode_status
2023-06-30 17:34:17.586671+00:00 [info] <0.221.0> Feature flags:   [ ] quorum_queue
2023-06-30 17:34:17.586878+00:00 [info] <0.221.0> Feature flags:   [ ] stream_queue
2023-06-30 17:34:17.586979+00:00 [info] <0.221.0> Feature flags:   [ ] user_limits
2023-06-30 17:34:17.587169+00:00 [info] <0.221.0> Feature flags:   [ ] virtual_host_metadata
2023-06-30 17:34:17.587332+00:00 [info] <0.221.0> Feature flags: feature flag states written to disk: yes
2023-06-30 17:34:17.611053+00:00 [info] <0.221.0> Feature flag `empty_basic_get_metric`: supported, attempt to enable...
2023-06-30 17:34:17.611249+00:00 [info] <0.221.0> Feature flag `empty_basic_get_metric`: mark as enabled=state_changing
2023-06-30 17:34:17.613076+00:00 [info] <0.221.0> Feature flags: list of feature flags found:
2023-06-30 17:34:17.613208+00:00 [info] <0.221.0> Feature flags:   [x] classic_mirrored_queue_version
2023-06-30 17:34:17.617252+00:00 [info] <0.221.0> Feature flags:   [x] drop_unroutable_metric
2023-06-30 17:34:17.617363+00:00 [info] <0.221.0> Feature flags:   [~] empty_basic_get_metric
2023-06-30 17:34:17.617442+00:00 [info] <0.221.0> Feature flags:   [ ] implicit_default_bindings
2023-06-30 17:34:17.617486+00:00 [info] <0.221.0> Feature flags:   [ ] maintenance_mode_status
2023-06-30 17:34:17.617529+00:00 [info] <0.221.0> Feature flags:   [ ] quorum_queue
2023-06-30 17:34:17.617565+00:00 [info] <0.221.0> Feature flags:   [ ] stream_queue
2023-06-30 17:34:17.618385+00:00 [info] <0.221.0> Feature flags:   [ ] user_limits
2023-06-30 17:34:17.618431+00:00 [info] <0.221.0> Feature flags:   [ ] virtual_host_metadata
2023-06-30 17:34:17.618478+00:00 [info] <0.221.0> Feature flags: feature flag states written to disk: yes
2023-06-30 17:34:17.785959+00:00 [info] <0.221.0> Feature flag `empty_basic_get_metric`: mark as enabled=true
2023-06-30 17:34:17.831807+00:00 [info] <0.221.0> Feature flags: list of feature flags found:
2023-06-30 17:34:17.831993+00:00 [info] <0.221.0> Feature flags:   [x] classic_mirrored_queue_version
2023-06-30 17:34:17.832037+00:00 [info] <0.221.0> Feature flags:   [x] drop_unroutable_metric
2023-06-30 17:34:17.832065+00:00 [info] <0.221.0> Feature flags:   [x] empty_basic_get_metric
2023-06-30 17:34:17.832103+00:00 [info] <0.221.0> Feature flags:   [ ] implicit_default_bindings
2023-06-30 17:34:17.837501+00:00 [info] <0.221.0> Feature flags:   [ ] maintenance_mode_status
2023-06-30 17:34:17.837584+00:00 [info] <0.221.0> Feature flags:   [ ] quorum_queue
2023-06-30 17:34:17.838586+00:00 [info] <0.221.0> Feature flags:   [ ] stream_queue
2023-06-30 17:34:17.838693+00:00 [info] <0.221.0> Feature flags:   [ ] user_limits
2023-06-30 17:34:17.838740+00:00 [info] <0.221.0> Feature flags:   [ ] virtual_host_metadata
2023-06-30 17:34:17.838797+00:00 [info] <0.221.0> Feature flags: feature flag states written to disk: yes
2023-06-30 17:34:17.996578+00:00 [info] <0.221.0> Feature flag `implicit_default_bindings`: supported, attempt to enable...
2023-06-30 17:34:17.996729+00:00 [info] <0.221.0> Feature flag `implicit_default_bindings`: mark as enabled=state_changing
2023-06-30 17:34:18.052555+00:00 [info] <0.221.0> Feature flags: list of feature flags found:
2023-06-30 17:34:18.052958+00:00 [info] <0.221.0> Feature flags:   [x] classic_mirrored_queue_version
2023-06-30 17:34:18.053030+00:00 [info] <0.221.0> Feature flags:   [x] drop_unroutable_metric
2023-06-30 17:34:18.053096+00:00 [info] <0.221.0> Feature flags:   [x] empty_basic_get_metric
2023-06-30 17:34:18.053138+00:00 [info] <0.221.0> Feature flags:   [~] implicit_default_bindings
2023-06-30 17:34:18.053176+00:00 [info] <0.221.0> Feature flags:   [ ] maintenance_mode_status
2023-06-30 17:34:18.053286+00:00 [info] <0.221.0> Feature flags:   [ ] quorum_queue
2023-06-30 17:34:18.053349+00:00 [info] <0.221.0> Feature flags:   [ ] stream_queue
2023-06-30 17:34:18.053421+00:00 [info] <0.221.0> Feature flags:   [ ] user_limits
2023-06-30 17:34:18.053459+00:00 [info] <0.221.0> Feature flags:   [ ] virtual_host_metadata
2023-06-30 17:34:18.053500+00:00 [info] <0.221.0> Feature flags: feature flag states written to disk: yes
2023-06-30 17:34:18.188674+00:00 [info] <0.221.0> Waiting for Mnesia tables for 30000 ms, 0 retries left
2023-06-30 17:34:18.189301+00:00 [info] <0.221.0> Successfully synced tables from a peer
2023-06-30 17:34:18.189450+00:00 [info] <0.221.0> Feature flag `implicit_default_bindings`: mark as enabled=true
2023-06-30 17:34:18.249730+00:00 [info] <0.221.0> Feature flags: list of feature flags found:
2023-06-30 17:34:18.249885+00:00 [info] <0.221.0> Feature flags:   [x] classic_mirrored_queue_version
2023-06-30 17:34:18.250009+00:00 [info] <0.221.0> Feature flags:   [x] drop_unroutable_metric
2023-06-30 17:34:18.250158+00:00 [info] <0.221.0> Feature flags:   [x] empty_basic_get_metric
2023-06-30 17:34:18.250212+00:00 [info] <0.221.0> Feature flags:   [x] implicit_default_bindings
2023-06-30 17:34:18.250251+00:00 [info] <0.221.0> Feature flags:   [ ] maintenance_mode_status
2023-06-30 17:34:18.250336+00:00 [info] <0.221.0> Feature flags:   [ ] quorum_queue
2023-06-30 17:34:18.250380+00:00 [info] <0.221.0> Feature flags:   [ ] stream_queue
2023-06-30 17:34:18.250436+00:00 [info] <0.221.0> Feature flags:   [ ] user_limits
2023-06-30 17:34:18.250834+00:00 [info] <0.221.0> Feature flags:   [ ] virtual_host_metadata
2023-06-30 17:34:18.250971+00:00 [info] <0.221.0> Feature flags: feature flag states written to disk: yes
2023-06-30 17:34:18.312801+00:00 [info] <0.221.0> Feature flag `maintenance_mode_status`: supported, attempt to enable...
2023-06-30 17:34:18.313899+00:00 [info] <0.221.0> Feature flag `maintenance_mode_status`: mark as enabled=state_changing
2023-06-30 17:34:18.328203+00:00 [info] <0.221.0> Feature flags: list of feature flags found:
2023-06-30 17:34:18.328321+00:00 [info] <0.221.0> Feature flags:   [x] classic_mirrored_queue_version
2023-06-30 17:34:18.328428+00:00 [info] <0.221.0> Feature flags:   [x] drop_unroutable_metric
2023-06-30 17:34:18.328699+00:00 [info] <0.221.0> Feature flags:   [x] empty_basic_get_metric
2023-06-30 17:34:18.328753+00:00 [info] <0.221.0> Feature flags:   [x] implicit_default_bindings
2023-06-30 17:34:18.328799+00:00 [info] <0.221.0> Feature flags:   [~] maintenance_mode_status
2023-06-30 17:34:18.328943+00:00 [info] <0.221.0> Feature flags:   [ ] quorum_queue
2023-06-30 17:34:18.329027+00:00 [info] <0.221.0> Feature flags:   [ ] stream_queue
2023-06-30 17:34:18.329072+00:00 [info] <0.221.0> Feature flags:   [ ] user_limits
2023-06-30 17:34:18.329111+00:00 [info] <0.221.0> Feature flags:   [ ] virtual_host_metadata
2023-06-30 17:34:18.329176+00:00 [info] <0.221.0> Feature flags: feature flag states written to disk: yes
2023-06-30 17:34:18.413958+00:00 [info] <0.221.0> Creating table rabbit_node_maintenance_states for feature flag `maintenance_mode_status`
2023-06-30 17:34:18.464988+00:00 [info] <0.221.0> Feature flag `maintenance_mode_status`: mark as enabled=true
2023-06-30 17:34:18.488211+00:00 [info] <0.221.0> Feature flags: list of feature flags found:
2023-06-30 17:34:18.498343+00:00 [info] <0.221.0> Feature flags:   [x] classic_mirrored_queue_version
2023-06-30 17:34:18.498424+00:00 [info] <0.221.0> Feature flags:   [x] drop_unroutable_metric
2023-06-30 17:34:18.498470+00:00 [info] <0.221.0> Feature flags:   [x] empty_basic_get_metric
2023-06-30 17:34:18.498518+00:00 [info] <0.221.0> Feature flags:   [x] implicit_default_bindings
2023-06-30 17:34:18.498561+00:00 [info] <0.221.0> Feature flags:   [x] maintenance_mode_status
2023-06-30 17:34:18.514068+00:00 [info] <0.221.0> Feature flags:   [ ] quorum_queue
2023-06-30 17:34:18.514310+00:00 [info] <0.221.0> Feature flags:   [ ] stream_queue
2023-06-30 17:34:18.514394+00:00 [info] <0.221.0> Feature flags:   [ ] user_limits
2023-06-30 17:34:18.514458+00:00 [info] <0.221.0> Feature flags:   [ ] virtual_host_metadata
2023-06-30 17:34:18.514617+00:00 [info] <0.221.0> Feature flags: feature flag states written to disk: yes
2023-06-30 17:34:18.679019+00:00 [info] <0.221.0> Feature flag `quorum_queue`: supported, attempt to enable...
2023-06-30 17:34:18.679162+00:00 [info] <0.221.0> Feature flag `quorum_queue`: mark as enabled=state_changing
2023-06-30 17:34:18.681463+00:00 [info] <0.221.0> Feature flags: list of feature flags found:
2023-06-30 17:34:18.681711+00:00 [info] <0.221.0> Feature flags:   [x] classic_mirrored_queue_version
2023-06-30 17:34:18.681775+00:00 [info] <0.221.0> Feature flags:   [x] drop_unroutable_metric
2023-06-30 17:34:18.681825+00:00 [info] <0.221.0> Feature flags:   [x] empty_basic_get_metric
2023-06-30 17:34:18.681868+00:00 [info] <0.221.0> Feature flags:   [x] implicit_default_bindings
2023-06-30 17:34:18.682082+00:00 [info] <0.221.0> Feature flags:   [x] maintenance_mode_status
2023-06-30 17:34:18.762213+00:00 [info] <0.221.0> Feature flags:   [~] quorum_queue
2023-06-30 17:34:18.762283+00:00 [info] <0.221.0> Feature flags:   [ ] stream_queue
2023-06-30 17:34:18.762357+00:00 [info] <0.221.0> Feature flags:   [ ] user_limits
2023-06-30 17:34:18.762395+00:00 [info] <0.221.0> Feature flags:   [ ] virtual_host_metadata
2023-06-30 17:34:18.762545+00:00 [info] <0.221.0> Feature flags: feature flag states written to disk: yes
2023-06-30 17:34:18.888555+00:00 [info] <0.221.0> Waiting for Mnesia tables for 30000 ms, 9 retries left
2023-06-30 17:34:18.890845+00:00 [info] <0.221.0> Successfully synced tables from a peer
2023-06-30 17:34:18.890992+00:00 [info] <0.221.0> Feature flag `quorum_queue`:   migrating Mnesia table rabbit_queue...
2023-06-30 17:34:19.122993+00:00 [info] <0.221.0> Feature flag `quorum_queue`:   migrating Mnesia table rabbit_durable_queue...
2023-06-30 17:34:19.230644+00:00 [info] <0.221.0> Feature flag `quorum_queue`:   Mnesia tables migration done
2023-06-30 17:34:19.230874+00:00 [info] <0.221.0> Feature flag `quorum_queue`: mark as enabled=true
2023-06-30 17:34:19.254091+00:00 [info] <0.221.0> Feature flags: list of feature flags found:
2023-06-30 17:34:19.254198+00:00 [info] <0.221.0> Feature flags:   [x] classic_mirrored_queue_version
2023-06-30 17:34:19.254235+00:00 [info] <0.221.0> Feature flags:   [x] drop_unroutable_metric
2023-06-30 17:34:19.254314+00:00 [info] <0.221.0> Feature flags:   [x] empty_basic_get_metric
2023-06-30 17:34:19.254344+00:00 [info] <0.221.0> Feature flags:   [x] implicit_default_bindings
2023-06-30 17:34:19.254369+00:00 [info] <0.221.0> Feature flags:   [x] maintenance_mode_status
2023-06-30 17:34:19.254452+00:00 [info] <0.221.0> Feature flags:   [x] quorum_queue
2023-06-30 17:34:19.254758+00:00 [info] <0.221.0> Feature flags:   [ ] stream_queue
2023-06-30 17:34:19.254814+00:00 [info] <0.221.0> Feature flags:   [ ] user_limits
2023-06-30 17:34:19.254878+00:00 [info] <0.221.0> Feature flags:   [ ] virtual_host_metadata
2023-06-30 17:34:19.254922+00:00 [info] <0.221.0> Feature flags: feature flag states written to disk: yes
2023-06-30 17:34:19.358776+00:00 [info] <0.221.0> Feature flag `stream_queue`: supported, attempt to enable...
2023-06-30 17:34:19.358927+00:00 [info] <0.221.0> Feature flag `stream_queue`: mark as enabled=state_changing
2023-06-30 17:34:19.362442+00:00 [info] <0.221.0> Feature flags: list of feature flags found:
2023-06-30 17:34:19.362990+00:00 [info] <0.221.0> Feature flags:   [x] classic_mirrored_queue_version
2023-06-30 17:34:19.363061+00:00 [info] <0.221.0> Feature flags:   [x] drop_unroutable_metric
2023-06-30 17:34:19.363112+00:00 [info] <0.221.0> Feature flags:   [x] empty_basic_get_metric
2023-06-30 17:34:19.363175+00:00 [info] <0.221.0> Feature flags:   [x] implicit_default_bindings
2023-06-30 17:34:19.363241+00:00 [info] <0.221.0> Feature flags:   [x] maintenance_mode_status
2023-06-30 17:34:19.363291+00:00 [info] <0.221.0> Feature flags:   [x] quorum_queue
2023-06-30 17:34:19.363337+00:00 [info] <0.221.0> Feature flags:   [~] stream_queue
2023-06-30 17:34:19.367963+00:00 [info] <0.221.0> Feature flags:   [ ] user_limits
2023-06-30 17:34:19.368021+00:00 [info] <0.221.0> Feature flags:   [ ] virtual_host_metadata
2023-06-30 17:34:19.369106+00:00 [info] <0.221.0> Feature flags: feature flag states written to disk: yes
2023-06-30 17:34:19.483130+00:00 [info] <0.221.0> Feature flag `stream_queue`: mark as enabled=true
2023-06-30 17:34:19.587581+00:00 [info] <0.221.0> Feature flags: list of feature flags found:
2023-06-30 17:34:19.589150+00:00 [info] <0.221.0> Feature flags:   [x] classic_mirrored_queue_version
2023-06-30 17:34:19.589213+00:00 [info] <0.221.0> Feature flags:   [x] drop_unroutable_metric
2023-06-30 17:34:19.589254+00:00 [info] <0.221.0> Feature flags:   [x] empty_basic_get_metric
2023-06-30 17:34:19.589339+00:00 [info] <0.221.0> Feature flags:   [x] implicit_default_bindings
2023-06-30 17:34:19.589381+00:00 [info] <0.221.0> Feature flags:   [x] maintenance_mode_status
2023-06-30 17:34:19.589421+00:00 [info] <0.221.0> Feature flags:   [x] quorum_queue
2023-06-30 17:34:19.589460+00:00 [info] <0.221.0> Feature flags:   [x] stream_queue
2023-06-30 17:34:19.589673+00:00 [info] <0.221.0> Feature flags:   [ ] user_limits
2023-06-30 17:34:19.597309+00:00 [info] <0.221.0> Feature flags:   [ ] virtual_host_metadata
2023-06-30 17:34:19.601754+00:00 [info] <0.221.0> Feature flags: feature flag states written to disk: yes
2023-06-30 17:34:19.681271+00:00 [info] <0.221.0> Feature flag `user_limits`: supported, attempt to enable...
2023-06-30 17:34:19.681467+00:00 [info] <0.221.0> Feature flag `user_limits`: mark as enabled=state_changing
2023-06-30 17:34:19.724505+00:00 [info] <0.221.0> Feature flags: list of feature flags found:
2023-06-30 17:34:19.724668+00:00 [info] <0.221.0> Feature flags:   [x] classic_mirrored_queue_version
2023-06-30 17:34:19.724728+00:00 [info] <0.221.0> Feature flags:   [x] drop_unroutable_metric
2023-06-30 17:34:19.724803+00:00 [info] <0.221.0> Feature flags:   [x] empty_basic_get_metric
2023-06-30 17:34:19.724843+00:00 [info] <0.221.0> Feature flags:   [x] implicit_default_bindings
2023-06-30 17:34:19.724885+00:00 [info] <0.221.0> Feature flags:   [x] maintenance_mode_status
2023-06-30 17:34:19.725115+00:00 [info] <0.221.0> Feature flags:   [x] quorum_queue
2023-06-30 17:34:19.728205+00:00 [info] <0.221.0> Feature flags:   [x] stream_queue
2023-06-30 17:34:19.734686+00:00 [info] <0.221.0> Feature flags:   [~] user_limits
2023-06-30 17:34:19.734834+00:00 [info] <0.221.0> Feature flags:   [ ] virtual_host_metadata
2023-06-30 17:34:19.734894+00:00 [info] <0.221.0> Feature flags: feature flag states written to disk: yes
2023-06-30 17:34:19.810254+00:00 [info] <0.221.0> Waiting for Mnesia tables for 30000 ms, 9 retries left
2023-06-30 17:34:19.813713+00:00 [info] <0.221.0> Successfully synced tables from a peer
2023-06-30 17:34:19.935551+00:00 [info] <0.221.0> Feature flag `user_limits`: mark as enabled=true
2023-06-30 17:34:19.952882+00:00 [info] <0.221.0> Feature flags: list of feature flags found:
2023-06-30 17:34:19.952996+00:00 [info] <0.221.0> Feature flags:   [x] classic_mirrored_queue_version
2023-06-30 17:34:19.953032+00:00 [info] <0.221.0> Feature flags:   [x] drop_unroutable_metric
2023-06-30 17:34:19.953059+00:00 [info] <0.221.0> Feature flags:   [x] empty_basic_get_metric
2023-06-30 17:34:19.953109+00:00 [info] <0.221.0> Feature flags:   [x] implicit_default_bindings
2023-06-30 17:34:19.953136+00:00 [info] <0.221.0> Feature flags:   [x] maintenance_mode_status
2023-06-30 17:34:19.953174+00:00 [info] <0.221.0> Feature flags:   [x] quorum_queue
2023-06-30 17:34:19.953200+00:00 [info] <0.221.0> Feature flags:   [x] stream_queue
2023-06-30 17:34:19.953261+00:00 [info] <0.221.0> Feature flags:   [x] user_limits
2023-06-30 17:34:19.953286+00:00 [info] <0.221.0> Feature flags:   [ ] virtual_host_metadata
2023-06-30 17:34:19.953311+00:00 [info] <0.221.0> Feature flags: feature flag states written to disk: yes
2023-06-30 17:34:20.078835+00:00 [info] <0.221.0> Feature flag `virtual_host_metadata`: supported, attempt to enable...
2023-06-30 17:34:20.079270+00:00 [info] <0.221.0> Feature flag `virtual_host_metadata`: mark as enabled=state_changing
2023-06-30 17:34:20.084762+00:00 [info] <0.221.0> Feature flags: list of feature flags found:
2023-06-30 17:34:20.084955+00:00 [info] <0.221.0> Feature flags:   [x] classic_mirrored_queue_version
2023-06-30 17:34:20.085022+00:00 [info] <0.221.0> Feature flags:   [x] drop_unroutable_metric
2023-06-30 17:34:20.123619+00:00 [info] <0.221.0> Feature flags:   [x] empty_basic_get_metric
2023-06-30 17:34:20.123670+00:00 [info] <0.221.0> Feature flags:   [x] implicit_default_bindings
2023-06-30 17:34:20.123709+00:00 [info] <0.221.0> Feature flags:   [x] maintenance_mode_status
2023-06-30 17:34:20.123795+00:00 [info] <0.221.0> Feature flags:   [x] quorum_queue
2023-06-30 17:34:20.123868+00:00 [info] <0.221.0> Feature flags:   [x] stream_queue
2023-06-30 17:34:20.123904+00:00 [info] <0.221.0> Feature flags:   [x] user_limits
2023-06-30 17:34:20.123938+00:00 [info] <0.221.0> Feature flags:   [~] virtual_host_metadata
2023-06-30 17:34:20.129496+00:00 [info] <0.221.0> Feature flags: feature flag states written to disk: yes
2023-06-30 17:34:20.762339+00:00 [info] <0.221.0> Waiting for Mnesia tables for 30000 ms, 9 retries left
2023-06-30 17:34:20.764058+00:00 [info] <0.221.0> Successfully synced tables from a peer
2023-06-30 17:34:20.954333+00:00 [info] <0.221.0> Feature flag `virtual_host_metadata`: mark as enabled=true
2023-06-30 17:34:20.971476+00:00 [info] <0.221.0> Feature flags: list of feature flags found:
2023-06-30 17:34:20.972331+00:00 [info] <0.221.0> Feature flags:   [x] classic_mirrored_queue_version
2023-06-30 17:34:20.974129+00:00 [info] <0.221.0> Feature flags:   [x] drop_unroutable_metric
2023-06-30 17:34:20.974567+00:00 [info] <0.221.0> Feature flags:   [x] empty_basic_get_metric
2023-06-30 17:34:20.975869+00:00 [info] <0.221.0> Feature flags:   [x] implicit_default_bindings
2023-06-30 17:34:20.976144+00:00 [info] <0.221.0> Feature flags:   [x] maintenance_mode_status
2023-06-30 17:34:20.976385+00:00 [info] <0.221.0> Feature flags:   [x] quorum_queue
2023-06-30 17:34:20.985341+00:00 [info] <0.221.0> Feature flags:   [x] stream_queue
2023-06-30 17:34:20.985453+00:00 [info] <0.221.0> Feature flags:   [x] user_limits
2023-06-30 17:34:20.985503+00:00 [info] <0.221.0> Feature flags:   [x] virtual_host_metadata
2023-06-30 17:34:20.985546+00:00 [info] <0.221.0> Feature flags: feature flag states written to disk: yes
2023-06-30 17:34:21.115745+00:00 [info] <0.221.0> Waiting for Mnesia tables for 30000 ms, 9 retries left
2023-06-30 17:34:21.116040+00:00 [info] <0.221.0> Successfully synced tables from a peer
2023-06-30 17:34:21.299833+00:00 [info] <0.221.0> Waiting for Mnesia tables for 30000 ms, 9 retries left
2023-06-30 17:34:21.300111+00:00 [info] <0.221.0> Successfully synced tables from a peer
2023-06-30 17:34:21.300184+00:00 [info] <0.221.0> Peer discovery backend rabbit_peer_discovery_classic_config does not support registration, skipping registration.
2023-06-30 17:34:21.300272+00:00 [info] <0.221.0> Will try to unlock with peer discovery backend rabbit_peer_discovery_classic_config
2023-06-30 17:34:21.300468+00:00 [info] <0.221.0> Running boot step database_sync defined by app rabbit
2023-06-30 17:34:21.300694+00:00 [info] <0.221.0> Running boot step feature_flags defined by app rabbit
2023-06-30 17:34:21.338224+00:00 [info] <0.221.0> Running boot step codec_correctness_check defined by app rabbit
2023-06-30 17:34:21.338352+00:00 [info] <0.221.0> Running boot step external_infrastructure defined by app rabbit
2023-06-30 17:34:21.342333+00:00 [info] <0.221.0> Running boot step rabbit_registry defined by app rabbit
2023-06-30 17:34:21.342824+00:00 [info] <0.221.0> Running boot step rabbit_auth_mechanism_cr_demo defined by app rabbit
2023-06-30 17:34:21.343205+00:00 [info] <0.221.0> Running boot step rabbit_queue_location_random defined by app rabbit
2023-06-30 17:34:21.343375+00:00 [info] <0.221.0> Running boot step rabbit_event defined by app rabbit
2023-06-30 17:34:21.352964+00:00 [info] <0.221.0> Running boot step rabbit_auth_mechanism_amqplain defined by app rabbit
2023-06-30 17:34:21.353234+00:00 [info] <0.221.0> Running boot step rabbit_auth_mechanism_plain defined by app rabbit
2023-06-30 17:34:21.353365+00:00 [info] <0.221.0> Running boot step rabbit_exchange_type_direct defined by app rabbit
2023-06-30 17:34:21.362955+00:00 [info] <0.221.0> Running boot step rabbit_exchange_type_fanout defined by app rabbit
2023-06-30 17:34:21.363138+00:00 [info] <0.221.0> Running boot step rabbit_exchange_type_headers defined by app rabbit
2023-06-30 17:34:21.363295+00:00 [info] <0.221.0> Running boot step rabbit_exchange_type_topic defined by app rabbit
2023-06-30 17:34:21.363383+00:00 [info] <0.221.0> Running boot step rabbit_mirror_queue_mode_all defined by app rabbit
2023-06-30 17:34:21.363463+00:00 [info] <0.221.0> Running boot step rabbit_mirror_queue_mode_exactly defined by app rabbit
2023-06-30 17:34:21.363565+00:00 [info] <0.221.0> Running boot step rabbit_mirror_queue_mode_nodes defined by app rabbit
2023-06-30 17:34:21.400801+00:00 [info] <0.221.0> Running boot step rabbit_priority_queue defined by app rabbit
2023-06-30 17:34:21.400929+00:00 [info] <0.221.0> Priority queues enabled, real BQ is rabbit_variable_queue
2023-06-30 17:34:21.401092+00:00 [info] <0.221.0> Running boot step rabbit_queue_location_client_local defined by app rabbit
2023-06-30 17:34:21.401244+00:00 [info] <0.221.0> Running boot step rabbit_queue_location_min_masters defined by app rabbit
2023-06-30 17:34:21.401378+00:00 [info] <0.221.0> Running boot step kernel_ready defined by app rabbit
2023-06-30 17:34:21.401695+00:00 [info] <0.221.0> Running boot step rabbit_sysmon_minder defined by app rabbit
2023-06-30 17:34:21.402464+00:00 [info] <0.221.0> Running boot step rabbit_epmd_monitor defined by app rabbit
2023-06-30 17:34:21.448988+00:00 [info] <0.568.0> epmd monitor knows us, inter-node communication (distribution) port: 25672
2023-06-30 17:34:21.449413+00:00 [info] <0.221.0> Running boot step guid_generator defined by app rabbit
2023-06-30 17:34:21.480870+00:00 [info] <0.221.0> Running boot step rabbit_node_monitor defined by app rabbit
2023-06-30 17:34:21.481474+00:00 [info] <0.572.0> Starting rabbit_node_monitor
2023-06-30 17:34:21.481865+00:00 [info] <0.221.0> Running boot step delegate_sup defined by app rabbit
2023-06-30 17:34:21.484047+00:00 [info] <0.221.0> Running boot step rabbit_memory_monitor defined by app rabbit
2023-06-30 17:34:21.484625+00:00 [info] <0.221.0> Running boot step rabbit_fifo_dlx_sup defined by app rabbit
2023-06-30 17:34:21.484903+00:00 [info] <0.221.0> Running boot step core_initialized defined by app rabbit
2023-06-30 17:34:21.484975+00:00 [info] <0.221.0> Running boot step upgrade_queues defined by app rabbit
2023-06-30 17:34:21.607289+00:00 [info] <0.221.0> message_store upgrades: 1 to apply
2023-06-30 17:34:21.609176+00:00 [info] <0.221.0> message_store upgrades: Applying rabbit_variable_queue:move_messages_to_vhost_store
2023-06-30 17:34:21.609673+00:00 [info] <0.221.0> message_store upgrades: No durable queues found. Skipping message store migration
2023-06-30 17:34:21.609956+00:00 [info] <0.221.0> message_store upgrades: Removing the old message store data
2023-06-30 17:34:21.651076+00:00 [info] <0.221.0> message_store upgrades: All upgrades applied successfully
2023-06-30 17:34:21.775782+00:00 [info] <0.221.0> Running boot step channel_tracking defined by app rabbit
2023-06-30 17:34:21.805945+00:00 [info] <0.221.0> Setting up a table for channel tracking on this node: tracked_channel_on_node_rabbit@2b6eb27dd567
2023-06-30 17:34:21.837092+00:00 [info] <0.221.0> Setting up a table for channel tracking on this node: tracked_channel_table_per_user_on_node_rabbit@2b6eb27dd567
2023-06-30 17:34:21.838071+00:00 [info] <0.221.0> Running boot step rabbit_channel_tracking_handler defined by app rabbit
2023-06-30 17:34:21.838988+00:00 [info] <0.221.0> Running boot step connection_tracking defined by app rabbit
2023-06-30 17:34:21.959051+00:00 [info] <0.221.0> Setting up a table for connection tracking on this node: tracked_connection_on_node_rabbit@2b6eb27dd567
2023-06-30 17:34:22.006458+00:00 [info] <0.221.0> Setting up a table for per-vhost connection counting on this node: tracked_connection_per_vhost_on_node_rabbit@2b6eb27dd567
2023-06-30 17:34:22.072286+00:00 [info] <0.221.0> Setting up a table for per-user connection counting on this node: tracked_connection_table_per_user_on_node_rabbit@2b6eb27dd567
2023-06-30 17:34:22.074361+00:00 [info] <0.221.0> Running boot step rabbit_connection_tracking_handler defined by app rabbit
2023-06-30 17:34:22.074797+00:00 [info] <0.221.0> Running boot step rabbit_definitions_hashing defined by app rabbit
2023-06-30 17:34:22.075030+00:00 [info] <0.221.0> Running boot step rabbit_exchange_parameters defined by app rabbit
2023-06-30 17:34:22.075251+00:00 [info] <0.221.0> Running boot step rabbit_mirror_queue_misc defined by app rabbit
2023-06-30 17:34:22.087175+00:00 [info] <0.221.0> Running boot step rabbit_policies defined by app rabbit
2023-06-30 17:34:22.125476+00:00 [info] <0.221.0> Running boot step rabbit_policy defined by app rabbit
2023-06-30 17:34:22.125766+00:00 [info] <0.221.0> Running boot step rabbit_queue_location_validator defined by app rabbit
2023-06-30 17:34:22.125904+00:00 [info] <0.221.0> Running boot step rabbit_quorum_memory_manager defined by app rabbit
2023-06-30 17:34:22.125988+00:00 [info] <0.221.0> Running boot step rabbit_stream_coordinator defined by app rabbit
2023-06-30 17:34:22.126347+00:00 [info] <0.221.0> Running boot step rabbit_vhost_limit defined by app rabbit
2023-06-30 17:34:22.126475+00:00 [info] <0.221.0> Running boot step rabbit_mgmt_reset_handler defined by app rabbitmq_management
2023-06-30 17:34:22.126701+00:00 [info] <0.221.0> Running boot step rabbit_mgmt_db_handler defined by app rabbitmq_management_agent
2023-06-30 17:34:22.126766+00:00 [info] <0.221.0> Management plugin: using rates mode 'basic'
2023-06-30 17:34:22.127371+00:00 [info] <0.221.0> Running boot step recovery defined by app rabbit
2023-06-30 17:34:22.138992+00:00 [info] <0.221.0> Running boot step empty_db_check defined by app rabbit
2023-06-30 17:34:22.139442+00:00 [info] <0.221.0> Will seed default virtual host and user...
2023-06-30 17:34:22.168841+00:00 [info] <0.221.0> Adding vhost '/' (description: 'Default virtual host', tags: [])
2023-06-30 17:34:22.329641+00:00 [info] <0.634.0> Making sure data directory '/var/lib/rabbitmq/mnesia/rabbit@2b6eb27dd567/msg_stores/vhosts/628WB79CIFDYO9LJI6DKMI09L' for vhost '/' exists
2023-06-30 17:34:22.379852+00:00 [info] <0.634.0> Setting segment_entry_count for vhost '/' with 0 queues to '2048'
2023-06-30 17:34:22.401937+00:00 [info] <0.634.0> Starting message stores for vhost '/'
2023-06-30 17:34:22.402333+00:00 [info] <0.639.0> Message store "628WB79CIFDYO9LJI6DKMI09L/msg_store_transient": using rabbit_msg_store_ets_index to provide index
2023-06-30 17:34:22.417358+00:00 [info] <0.634.0> Started message store of type transient for vhost '/'
2023-06-30 17:34:22.417698+00:00 [info] <0.643.0> Message store "628WB79CIFDYO9LJI6DKMI09L/msg_store_persistent": using rabbit_msg_store_ets_index to provide index
2023-06-30 17:34:22.433077+00:00 [warning] <0.643.0> Message store "628WB79CIFDYO9LJI6DKMI09L/msg_store_persistent": rebuilding indices from scratch
2023-06-30 17:34:22.438457+00:00 [info] <0.634.0> Started message store of type persistent for vhost '/'
2023-06-30 17:34:22.439242+00:00 [info] <0.634.0> Recovering 0 queues of type rabbit_classic_queue took 55ms
2023-06-30 17:34:22.439365+00:00 [info] <0.634.0> Recovering 0 queues of type rabbit_quorum_queue took 0ms
2023-06-30 17:34:22.439437+00:00 [info] <0.634.0> Recovering 0 queues of type rabbit_stream_queue took 0ms
2023-06-30 17:34:22.459104+00:00 [info] <0.221.0> Created user 'user'
2023-06-30 17:34:22.472005+00:00 [info] <0.221.0> Successfully set user tags for user 'user' to [administrator]
2023-06-30 17:34:22.516067+00:00 [info] <0.221.0> Successfully set permissions for 'user' in virtual host '/' to '.*', '.*', '.*'
2023-06-30 17:34:22.516354+00:00 [info] <0.221.0> Running boot step rabbit_looking_glass defined by app rabbit
2023-06-30 17:34:22.516441+00:00 [info] <0.221.0> Running boot step rabbit_core_metrics_gc defined by app rabbit
2023-06-30 17:34:22.517439+00:00 [info] <0.221.0> Running boot step background_gc defined by app rabbit
2023-06-30 17:34:22.519124+00:00 [info] <0.221.0> Running boot step routing_ready defined by app rabbit
2023-06-30 17:34:22.519203+00:00 [info] <0.221.0> Running boot step pre_flight defined by app rabbit
2023-06-30 17:34:22.519235+00:00 [info] <0.221.0> Running boot step notify_cluster defined by app rabbit
2023-06-30 17:34:22.521005+00:00 [info] <0.221.0> Running boot step networking defined by app rabbit
2023-06-30 17:34:22.521259+00:00 [info] <0.221.0> Running boot step rabbit_maintenance_mode_state defined by app rabbit
2023-06-30 17:34:22.521321+00:00 [info] <0.221.0> Creating table rabbit_node_maintenance_states for feature flag `maintenance_mode_status`
2023-06-30 17:34:22.532493+00:00 [info] <0.221.0> Running boot step definition_import_worker_pool defined by app rabbit
2023-06-30 17:34:22.532964+00:00 [info] <0.280.0> Starting worker pool 'definition_import_pool' with 4 processes in it
2023-06-30 17:34:22.534741+00:00 [info] <0.221.0> Running boot step cluster_name defined by app rabbit
2023-06-30 17:34:22.535101+00:00 [info] <0.221.0> Initialising internal cluster ID to 'rabbitmq-cluster-id-3EC3aXLvrXWw67gAEbyFaw'
2023-06-30 17:34:22.551935+00:00 [info] <0.221.0> Running boot step direct_client defined by app rabbit
2023-06-30 17:34:22.552259+00:00 [info] <0.221.0> Running boot step rabbit_management_load_definitions defined by app rabbitmq_management
2023-06-30 17:34:22.552438+00:00 [info] <0.677.0> Resetting node maintenance status
2023-06-30 17:34:22.708404+00:00 [info] <0.736.0> Management plugin: HTTP (non-TLS) listener started on port 15672
2023-06-30 17:34:22.708736+00:00 [info] <0.764.0> Statistics database started.
2023-06-30 17:34:22.711912+00:00 [info] <0.763.0> Starting worker pool 'management_worker_pool' with 3 processes in it
2023-06-30 17:34:22.795797+00:00 [info] <0.778.0> Prometheus metrics: HTTP (non-TLS) listener started on port 15692
2023-06-30 17:34:22.796227+00:00 [info] <0.677.0> Ready to start client connection listeners
2023-06-30 17:34:22.821136+00:00 [info] <0.822.0> started TCP listener on [::]:5672
 completed with 4 plugins.
2023-06-30 17:34:23.738441+00:00 [info] <0.677.0> Server startup complete; 4 plugins started.
2023-06-30 17:34:23.738441+00:00 [info] <0.677.0>  * rabbitmq_prometheus
2023-06-30 17:34:23.738441+00:00 [info] <0.677.0>  * rabbitmq_management
2023-06-30 17:34:23.738441+00:00 [info] <0.677.0>  * rabbitmq_web_dispatch
2023-06-30 17:34:23.738441+00:00 [info] <0.677.0>  * rabbitmq_management_agent
```

</details>

###### [Back to top](#contributing)

### Celery task-queue

Celery is currently being used as to process background jobs via a task-queue

If you are implementing a new task, you will need to restart All task-queue related
Automappa services (`redis`, `flower`, `web`, `celery`, `rabbitmq`)
as tasks are registered with celery at instantiation and will not be
'hot-reloaded' like other parts of the app.

For more information on implementing new tasks see the [task-queue docs](task-queue.md)

<details>

<summary>What to see at startup</summary>

```console
automappa-celery-1    |  
automappa-celery-1    |  -------------- celery@beade5f64d0f v5.3.0 (emerald-rush)
automappa-celery-1    | --- ***** ----- 
automappa-celery-1    | -- ******* ---- Linux-5.15.49-linuxkit-x86_64-with-glibc2.31 2023-06-09 11:18:28
automappa-celery-1    | - *** --- * --- 
automappa-celery-1    | - ** ---------- [config]
automappa-celery-1    | - ** ---------- .> app:         automappa.tasks:0x7f66305c1070
automappa-celery-1    | - ** ---------- .> transport:   amqp://user:**@rabbitmq:5672//
automappa-celery-1    | - ** ---------- .> results:     redis://redis:6379/0
automappa-celery-1    | - *** --- * --- .> concurrency: 2 (prefork)
automappa-celery-1    | -- ******* ---- .> task events: ON
automappa-celery-1    | --- ***** ----- 
automappa-celery-1    |  -------------- [queues]
automappa-celery-1    |                 .> celery           exchange=celery(direct) key=celery
automappa-celery-1    |                 
automappa-celery-1    | 
automappa-celery-1    | [tasks]
automappa-celery-1    |   . automappa.tasks.aggregate_embeddings
automappa-celery-1    |   . automappa.tasks.count_kmer
automappa-celery-1    |   . automappa.tasks.embed_kmer
automappa-celery-1    |   . automappa.tasks.get_embedding_traces_df
automappa-celery-1    |   . automappa.tasks.normalize_kmer
automappa-celery-1    |   . automappa.tasks.preprocess_clusters_geom_medians
automappa-celery-1    |   . automappa.tasks.preprocess_marker_symbols
automappa-celery-1    | 
```

</details>

###### [Back to top](#contributing)

### Redis

<details>

<summary>What to see at startup</summary>

```console
1:C 30 Jun 2023 16:28:07.865 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
1:C 30 Jun 2023 16:28:07.865 # Redis version=7.0.11, bits=64, commit=00000000, modified=0, pid=1, just started
1:C 30 Jun 2023 16:28:07.865 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
1:M 30 Jun 2023 16:28:07.867 * monotonic clock: POSIX clock_gettime
1:M 30 Jun 2023 16:28:07.868 * Running mode=standalone, port=6379.
1:M 30 Jun 2023 16:28:07.868 # Server initialized
1:M 30 Jun 2023 16:28:07.868 * Ready to accept connections
```

</details>

###### [Back to top](#contributing)

### Flower

<details>

<summary>What to see on successful startup</summary>

```console
DEBUG:automappa.tasks:celery config:
task_send_sent_event: True
task_track_started: True
worker_concurrency: 2
worker_prefetch_multiplier: 1
worker_send_task_events: True
broker_url: 'amqp://user:********@rabbitmq:5672//'
result_backend: 'redis://redis:6379/0'
deprecated_settings: None
INFO:flower.command:Visit me at http://0.0.0.0:5555
INFO:flower.command:Broker: amqp://user:**@rabbitmq:5672//
INFO:flower.command:Registered tasks: 
['automappa.tasks.aggregate_embeddings',
 'automappa.tasks.count_kmer',
 'automappa.tasks.embed_kmer',
 'automappa.tasks.get_embedding_traces_df',
 'automappa.tasks.normalize_kmer',
 'automappa.tasks.preprocess_clusters_geom_medians',
 'automappa.tasks.preprocess_marker_symbols',
 'celery.accumulate',
 'celery.backend_cleanup',
 'celery.chain',
 'celery.chord',
 'celery.chord_unlock',
 'celery.chunks',
 'celery.group',
 'celery.map',
 'celery.starmap']
INFO:kombu.mixins:Connected to amqp://user:**@rabbitmq:5672//
WARNING:flower.inspector:Inspect method registered failed
WARNING:flower.inspector:Inspect method active failed
WARNING:flower.inspector:Inspect method scheduled failed
WARNING:flower.inspector:Inspect method reserved failed
WARNING:flower.inspector:Inspect method active_queues failed
WARNING:flower.inspector:Inspect method conf failed
WARNING:flower.inspector:Inspect method stats failed
WARNING:flower.inspector:Inspect method revoked failed
```

</details>

###### [Back to top](#contributing)

## Development resources

### Libraries

- [dash-extensions docs](https://www.dash-extensions.com/ "dash-extensions documentation")
- [dash-extensions GitHub](https://github.com/thedirtyfew/dash-extensions "dash-extensions GitHub repository")
- [plotly Dash docs](https://dash.plotly.com/ "plotly Dash documentation")
- [dash-bootstrap-components docs](http://dash-bootstrap-components.opensource.faculty.ai/ "dash-bootstrap-components documentation")
- [dash-mantine-components docs](https://www.dash-mantine-components.com/ "dash-mantine-components documentation")
- [dash-iconify icons browser](<https://icon-sets.iconify.design/> "Iconify icon sets")

### Monitoring and Task-queue Services

#### Networking, backend and task management

- [docker-compose networking docs](<https://docs.docker.com/compose/networking/#links>)
- [live mongoDB dash example](<https://github.com/Coding-with-Adam/Dash-by-Plotly/blob/master/Dash_and_Databases/MongoDB/live-mongodb-dash.py>)
- [plotly dash `dcc.Store` docs](<https://dash.plotly.com/dash-core-components/store#store-clicks-example>)
- [how to access rabbitmq publicly](<https://stackoverflow.com/questions/23020908/how-to-access-rabbitmq-publicly> "how to access RabbitMQ publicly")
- [StackOverflow: how to access rabbitmq publicly](https://stackoverflow.com/a/57612615 "StackOverflow: how to access RabbitMQ publicly")
- [celery rabbitmq tutorial](https://suzannewang.com/celery-rabbitmq-tutorial/)

### Miscellaneous

dash logger is not supported with pattern matching callbacks

#### docker-compose services configuration

>NOTE: The Prometheus and Grafana services are disabled by default. You may enable them by removing the comments in the docker compose
file.

***NOTE: All of this assumes you have all docker services running via `make up` or `docker-compose up`***

> ~Provision grafana from `docker-compose.yml`. See: [Grafana provisioning example data source config file](https://grafana.com/docs/grafana/latest/administration/provisioning/#example-data-source-config-file)~
> Found a nice blog post and accompanying GitHub repo to follow:
>
> - [Medium blog post](https://medium.com/swlh/easy-grafana-and-docker-compose-setup-d0f6f9fcec13)
> - [github.com/annea-ai/grafana-infrastructure](<https://github.com/annea-ai/grafana-infrastructure>)
> - [Grafana docs on Provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/)

- RabbitMQ management - [http://localhost:15672](http://localhost:15672)
- Flower link - [http://localhost:5555](http://localhost:5555)
- Prometheus link - [http://localhost:9090](http://localhost:9090)
- Grafana link - [http://localhost:3000](http://localhost:3000)

#### Grafana configuration

- flower+prometheus+grafana [add prometheus as a data source in grafana](<https://flower.readthedocs.io/en/latest/prometheus-integration.html#add-prometheus-as-a-data-source-in-grafana> "flower+prometheus+grafana add prometheus as a data source in grafana")
- grafana link - [http://localhost:3000](http://localhost:3000)

Add the prometheus url as:

```bash
http://prometheus:9090
```

Notice the tutorial mentions `http://localhost:9090`, but since this is running as a service using `docker-compose` the hostname changes to the
`prometheus` alias (this is the name of the service in the `docker-compose.yml` file)

[Back to top](#contributing)

## Roadmap

### UI/UX enhancements

- [ ] Cytoscape intra/inter-MAG connection mapping
- [ ] Overplotting reduction toggle with MAG geometric medians

### Data processing

#### Pre-processing

- [ ] k-mer frequency analysis workflow
  - [ ] Parameter selection (submission to task-queue, progress monitoring & results retrieval)
- [ ] BGC annotation (some tools: [`gecco`](gecco url), [`AntiSMASH`](antismash url), etc.)

#### Post-processing

- [ ] [GTDB](GTDB url) taxon assignment
- [ ] [METABOLIC](METABOLIC url) functional assignment
- [ ] [CheckM](CheckM url) completeness/purity QA
- [ ] KEGG ortholog assignment (using [`kofamscan`](kofamscan url))

###### [Back to top](#contributing)
