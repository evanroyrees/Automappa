# Data

## Models

## Schema

## Loader

## Source

>TODO Create specific `DataSource`s according to methods from components
> i.e. `Scatterplot2dDataSource`

To increase cohesion we may want to separate `DataSource` into (for example):

- `MetagenomeDataSource`
- `MarkerDataSource`
- `ConnectionDataSource`
- `BinningDataSource`

Which should implement the methods defined in the ComponentDataSource protocols

```python
# CRUD metagenome
logger.info("Begin CRUD metagenome")
create_metagenome("data/lasonolide/metagenome.filtered.fna")
metagenomes = read_metagenomes()
logger.info("End CRUD metagenome")

# CRUD contigs
logger.info("Begin CRUD Contigs")
create_contigs("data/lasonolide/binning.tsv")
contigs = read_contigs(
    [
        "NODE_122095_length_595_cov_1.911111",
        "NODE_137073_length_558_cov_1.087475",
        "NODE_53038_length_961_cov_43.318985",
        "NODE_64513_length_857_cov_39.677057",
        "NODE_43271_length_1085_cov_2.514563",
    ]
)
logger.info("End CRUD Contigs")
# CRUD markers
logger.info("Begin CRUD Markers")
create_markers("data/lasonolide/bacteria.markers.tsv")
markers = read_markers()
logger.info("End CRUD Markers")

# CRUD cytoscape connections
logger.info("Begin CRUD cytoscape connections")
create_cytoscape_connections("data/lasonolide/cytoscape.connections.tab")
connections = read_cytoscape_connections()
logger.info("End CRUD cytoscape connections")
```
