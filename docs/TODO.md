# TODO (WIP)

## TODOs lists

### 🐰:carrot: task-queue

- [ ] Determine minimal task-queue case for setup/testing
- [ ] simple time.sleep(10) and generation of tasks table displaying progress
- [ ] pre-processing step for marker symbols and marker sizes based on marker counts in `Contig`
- [ ] k-mer freq. analysis steps

#### Data ingestion, CRUD Operations and UI

- [ ] create metagenome
- [ ] create contigs
- [ ] create markers
- [ ] create connections
- [ ] update each created to metagenome with sample name

#### 🐎 Component data pre-processing

- [ ] component to inform user of currently processing tasks (i.e. [Dash AG Grid](https://dash.plotly.com/dash-ag-grid/ "Dash AG grid component"), [notification](https://www.dash-mantine-components.com/components/notification "Dash mantine notification component"), etc.)
- [ ] marker symbol
- [ ] kmer embedding
- [ ] geometric medians
- [ ] MAG summary

### Pages

#### base Layout components

- [x] `metagenome_id_store = dcc.Store(ids.METAGENOME_ID_STORE, "data")`
  - [x] Pattern matching callback to get `metagenome_id` (or `Metagenome.name`) for
  selected sample card
  - [ ] Pattern matching callback to uncheck any other cards when a sample is selected

#### Home components

- [ ] loader "new sample" button disable during db ingestion
- [ ] Loader (or notification or overlay? on sample submit button click)
  - [ ] User notified on submit button click (will require task-queue)
  - [ ] Notification dismissed when database injestion finished (will require task-queue)
  
  Supposedly background callbacks here are not supported with notifications.
- [ ] :bug: new sample card rendered upon stepper sample submit button click
- [x] Synchronize pages using `metagenome_id` in a `dcc.Store(ids.METAGENOME_ID_STORE)`
  - [x] 🔗 Add callbacks for sample cards
  - [x] :fire: Remove button ~refine button navigates to `MAG-refinement`~
  - [x] :fire: Remove button ~summarize button navigates to `MAG-summary`~
  - [x] :link: "Card selected" option for storage in `ids.METAGENOME_ID_STORE`

#### MAG refinement components

- [x] Determine construction of `Refinement(SQLModel)`
- [x] Allow save MAG refinement after scatterplot selections
- [x] Allow table generation from saved refinements
- [x] Allow data download
- [ ] re-implement cytoscape contig connection graph callbacks
- [x] Connect `Input(ids.COVERAGE_RANGE_SLIDER, "value")` to 2D scatterplots
  > (End-user ? --> should 3D scatterplot also be updated?)

Component protocols:

> Following syntax: `class ComponentDataSource(Protocol)`

- [x] `class Scatterplot2dDataSource(Protocol)`
- [x] `class MarkerSymbolsLegendDataSource(Protocol)`
- [x] `class SaveSelectionsButtonDataSource(Protocol)`
- [ ] `class SettingsOffcanvasDataSource(Protocol)`
  - [x] `class Scatterplot2dAxesOptionsDataSource(Protocol)`
  - [x] `class ColorByColumnOptionsDataSource(Protocol)`
  - [ ] ~`class KmerNormMethodDropdownOptionsDataSource`~
  - [ ] ~`class KmerEmbedMethodDropdownOptionsDataSource`~
- [x] `class MagMetricsDataSource(Protocol)`
- [x] `class TaxonomyDistributionDataSource(Protocol)`
  - [ ] :fire: remove use of pandas in source method
- [x] `class Scatterplot3dDataSource(Protocol)`
- [x] `class CoverageRangeSliderDataSource(Protocol)`
- [x] `class CoverageBoxplotDataSource(Protocol)`
- [x] `class GcPercentBoxplotDataSource(Protocol)`
- [x] `class LengthBoxplotDataSource(Protocol)`
- [ ] `class ContigCytoscapeDataSource(Protocol)`
- [x] `class RefinementsTableDataSource(Protocol)`

#### MAG Summary components

Passed `DataSource` object:

- [ ] `class SummaryDataSource(BaseModel)`

Component protocols:

> Following syntax: `class ComponentDataSource(Protocol)`

- [x] `class CoverageBoxplotDataSource(Protocol)`
- [x] `class GcPercentBoxplotDataSource(Protocol)`
- [x] `class LengthBoxplotDataSource(Protocol)`
- [x] `class ClusterMetricsBarplotDataSource(Protocol)`
- [x] `class ClusterDropdownDataSource(Protocol)`
- [x] `class ClusterMetricsBoxplotDataSource(Protocol)`
- [x] `class ClusterStatsTableDataSource(Protocol)`
- [x] `class ClusterTaxonomyDistributionDataSource(Protocol)`

-----------------------------------------------------

## Development resources

### Libraries

- [dash-extensions docs](https://www.dash-extensions.com/ "dash-extensions documentation")
- [Dash Extensions Enrich Module](https://www.dash-extensions.com/getting-started/enrich)
- [dash-extensions GitHub](https://github.com/thedirtyfew/dash-extensions "dash-extensions GitHub repository")
- [dash-mantine-components docs](https://www.dash-mantine-components.com/ "dash-mantine-components documentation")
- [dash-iconify icons browser](<https://icon-sets.iconify.design/> "Iconify icon sets")
- [dash-bootstrap-components docs](http://dash-bootstrap-components.opensource.faculty.ai/ "dash-bootstrap-components documentation")
- [plotly Dash docs](https://dash.plotly.com/ "plotly Dash documentation")

### Services

#### Networking, backend and task management

- [docker-compose networking docs](<https://docs.docker.com/compose/networking/#links>)
- [live mongoDB dash example](<https://github.com/Coding-with-Adam/Dash-by-Plotly/blob/master/Dash_and_Databases/MongoDB/live-mongodb-dash.py>)
- [plotly dash `dcc.Store` docs](<https://dash.plotly.com/dash-core-components/store#store-clicks-example>)
- [how to access rabbitmq publicly](<https://stackoverflow.com/questions/23020908/how-to-access-rabbitmq-publicly> "how to access RabbitMQ publicly")
- [StackOverflow: how to access rabbitmq publicly](https://stackoverflow.com/a/57612615 "StackOverflow: how to access RabbitMQ publicly")

### Miscellaneous

dash logger is not supported with pattern matching callbacks
