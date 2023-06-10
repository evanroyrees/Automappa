# Contributing

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

## Pages

> If you are not adding a page to Automappa but simply a component to an existing page, you may skip this section.

Automappa uses a dash feature called [`pages`](https://dash.plotly.com/urls "dash pages documentation") to allow multi-page navigation
*without* having to explicitly define callbacks for rendering each page (more on this later).

Similarly, many useful dash utilities are also available in a package called
[`dash-extensions`](https://www.dash-extensions.com/ "dash extensions documentation")
which has been used throughout. Unfortunately these packages are not completely synchronized,
so the simple approach as described in the dash documentation may not be taken. However, some workarounds
are described in the [dash-extensions docs](https://www.dash-extensions.com/getting_started/enrich).

## Adding a new component

### 0. Before your begin

Checkout a new branch

```bash
git checkout -b <feature> develop
```

Change `SERVER_DEBUG = False` in `.env` to `SERVER_DEBUG = True`

### 1. Create a unique id for the component in `automappa/components/ids.py`

A unique id is required to specify what data should be set or retrieved based on the component being implemented.

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

### 2. Create your component file in the components sub-directory

The component should be placed respective to the page where it will be added.

i.e. `automappa/pages/<page>/components/your_component.py`

>NOTE: Try to be clear and concise when naming the component file

### 3. Create the standard `render` function in `your_component.py`

All components follow a standard syntax of a `render` function that takes at minimum the page's app (or `DashProxy`) as input.

You'll notice the type hint is a `DashProxy` object as the defined callback is being registered specifically to this.

To have a reactive component you will need to define a callback function that takes any number of `Input`s and `Output`s. Typically we'll only use one `Output` and may
have multiple `Inputs` to have our callback only perform one task. The function to
create a reactive component in the app may have an arbitrary name but I tend to
stick with something related to the type of reactivity of the component and what
property is being updated.

>NOTE: you will have to check your particular components documentation to determine
the properties that are available.

```python
from automappa.components import ids
from dash_extensions.enrich import DashProxy,html,dcc


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.COMPONENT_ID, "<component-property>"),
        Input(ids.<input_component_id>, "<component-property>"),
    )
    def your_component_callback(input_component_prop)
        ...
        return ...
    ...
    return html.Div(dcc.Component(id=ids.COMPONENT_ID, ...), ...)
```

>NOTE: The actual `app` object that will ultimately be passed to this is a `DashBlueprint` which is a wrapper
of `DashProxy` used similarly to flask blueprint templates. For more details on this see the
respective `automappa/pages/<page>/layout.py` file.

### 4. Import and render your component into the page layout

At this point, the majority of the work has been done, now all of you have to do is simply place your component
into the layout of the page. This should correspond to the same page you've implemented your component for:
`automappa/pages/<page>/layout.py`.

For more information on how to use `dbc.Row` and `dbc.Col` see the
[dash-bootstrap-components layout docs](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/)

```python
# contents of automappa/pages/<page>/layout.py
from automappa.pages.mag_refinement.components import your_component

def render() -> html.Div:
    ...
    # Include your component
    dbc.Row(dbc.Col(your_component.render(app)))
    ...
```

### 5. Update existing components to use `your_component` as an input

To retrieve information from components while interacting with the application
`dash` uses the `@app.callback(Output, Input)` syntax as we have seen.

>NOTE: There are other keywords that may be supplied to `@app.callback` and you can
find more information on this in the [Dash basic callbacks docs](<<https://dash.plotly.com/basic-callbacks> "Dash callbacks documentation") and [Dash advanced callbacks docs](https://dash.plotly.com/advanced-callbacks "Dash advanced callbacks documentation").

## Component implementation example

Here's a simple example to help describe the process.

Let's say we want to implement a [RangeSlider](https://dash.plotly.com/dash-core-components/rangeslider)
that we would like to put on the MAG refinement page to enable users to filter the 2d scatterplot.

To begin, we would create a new component id

### 1. Create component id

```python
# contents of automappa/components/ids.py
COVERAGE_RANGE_SLIDER_ID = "coverage-range-slider-id"
```

### 2. Create `coverage_range_slider.py` in `automappa/pages/mag_refinement/components`

### 3. Write component's `render` function

>NOTICE: any of the imports that would typically be `from dash import Input,Output,html`
are now `from dash_extensions.enrich import Input,Output,html`.
>This must be implemented throughout the entirety of the application
 to achieve the intended behaviors available through
the dash-extensions package.

```python
from automappa.components import ids
from dash_extensions.enrich import Output,Input,html,DashProxy,dcc


def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.COVERAGE_RANGE_SLIDER_ID, "max"),
        Input(ids.SELECTED_TABLES_STORE, "data"),
    )
    def get_max_coverage_value(sample: SampleTables):
        df: pd.DataFrame = sample.binning.table
        return df.coverage.max()
    return html.Div(
        dcc.RangeSlider(
            id=ids.COVERAGE_RANGE_SLIDER_ID,
            min=0,
            allowCross=False
        )
    )
```

### 4. include component in `automappa/pages/mag_refinement/layout.py`

```python
# Import the components
from automappa.pages.mag_refinement.components import (
    ...
    coverage_range_slider
    ...
)

def render() -> DashBlueprint:
    ...
    app.layout = dbc.Container(
        children=[
            ...
            # Render the component where you would like it in the layout
            dbc.Row(dbc.Col(coverage_range_slider.render(app))),
        ],
    )
    return app
```

### 5. Creating reactivity from the `RangeSlider` component (using this as an `Input`)

One example would be to include the range slider as an additional `Input` to
the scatterplot 2d component.

Now in the `automappa/pages/mag_refinement/components/scatterplot_2d.py` callback
we would include the range slider id as an input. i.e.

```python
def render(app: DashProxy) -> html.Div:
    @app.callback(
        Output(ids.SCATTERPLOT_2D, "figure"),
        [
            ...
            Input(ids.RANGE_SLIDER_ID, "value"), 
            # order here matters as this will correspond to the 
            # scatterplot_2d_figure_callback argument order
        ]
        
    )
    def scatterplot_2d_figure_callback(
        sample: SampleTables,
        ...
        range_slider_values: tuple[int,int] 
        # This argument should be in the same order as defined within the Input list
        # from @app.callback(Output, List[Input])
    )
    # Make sure we have integer values before filtering
    min_coverage,max_coverage = map(int, range_slider_values)
    # Filter scatterplot contigs by range slider coverage values
    bin_df = bin_df.loc[
        bin_df.coverage.ge(min_coverage)
        & bin_df.coverage.le(max_coverage)
    ]
    # proceed... with figure building...
```

## Some notes on available services

Currently Automappa utilizes multiple services to manage its backend database, task-queue and monitoring.

These services are:

| Service | Purpose |
| -: | :- |
| `postgres` | backend database to store/retrieve user uploaded data |
| `rabbitmq` | task-queue broker for managing worker tasks |
| `celery` | task-queue worker |
| `redis` |  task-queue broker & worker backend for passing tasks to/from the task-queue |
| `flower` | for monitoring `celery` and `rabbitmq` task-queue |
| `web` | The automappa web instance |
| \[Not currently in use\] `prometheus` | service monitoring dashboard |
| \[Not currently in use\] `grafana` | service monitoring dashboard |

You may find additional details on these services with their respective
docker image builds, Dockerfiles, commands, dependencies and their
ports in the `docker-compose.yml` file.

Customization of the urls to these services may be
performed by editing the `.env` files as many of
these settings are configured from here.

### Celery task-queue

Celery is currently being used as a task-queue and when instantiated you should see something like this:

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

>NOTE: If you are implementing a new task, you will need to restart this service
as tasks are registered with celery at instantiation and will not be
'hot-reloaded' like other parts of the app.

## Development resources

### Libraries

- [dash-extensions docs](https://www.dash-extensions.com/ "dash-extensions documentation")
- [dash-extensions GitHub](https://github.com/thedirtyfew/dash-extensions "dash-extensions GitHub repository")
- [plotly Dash docs](https://dash.plotly.com/ "plotly Dash documentation")
- [dash-bootstrap-components docs](http://dash-bootstrap-components.opensource.faculty.ai/ "dash-bootstrap-components documentation")
- [dash-mantine-components docs](https://www.dash-mantine-components.com/ "dash-mantine-components documentation")
- [dash-iconify icons browser](<https://icon-sets.iconify.design/> "Iconify icon sets")
