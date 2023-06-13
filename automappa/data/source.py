import itertools
from pydantic import BaseModel
from typing import List, Optional
from typing_extensions import Literal

from automappa.data.db import check_table_exists

from automappa.data.loader import get_table


class MetagenomeAnnotations(BaseModel):
    contig: str
    binning: Optional[str]
    refinements: Optional[str]
    markers: Optional[str]
    # marker_symbols: Union[AsyncResult,str]
    metagenome: Optional[str]


class AnnotationTable(BaseModel):
    id: str
    index_col: Optional[str] = "contig"

    @property
    def sample_checksum(self):
        return self.id.split("-")[0]

    @property
    def name(self):
        return "-".join(self.id.split("-")[1:])

    @property
    def table(self):
        return get_table(self.id, index_col=self.index_col)

    @property
    def exists(self):
        return check_table_exists(self.id)

    @property
    def columns(self):
        return self.table.columns


class KmerTable(BaseModel):
    assembly: AnnotationTable
    size: Literal[3, 4, 5] = 5
    norm_method: Literal["am_clr", "ilr", "clr"] = "am_clr"
    embed_dims: Optional[int] = 2
    # embed_dims: conint(gt=1, lt=100) = 2
    embed_method: Literal["bhsne", "sksne", "umap", "densmap", "trimap"] = "bhsne"

    @property
    def counts(self) -> AnnotationTable:
        return AnnotationTable(
            id=self.assembly.id.replace("-metagenome", f"-{self.size}mers")
        )

    @property
    def norm_freqs(self) -> AnnotationTable:
        return AnnotationTable(
            id=self.assembly.id.replace(
                "-metagenome", f"-{self.size}mers-{self.norm_method}"
            )
        )

    @property
    def embedding(self) -> AnnotationTable:
        return AnnotationTable(
            id=self.assembly.id.replace(
                "-metagenome",
                f"-{self.size}mers-{self.norm_method}-{self.embed_method}",
            )
        )


class CytoscapeConnectionsTable(BaseModel):
    id: str

    @property
    def sample_checksum(self):
        return self.id.split("-")[0]

    @property
    def name(self):
        return "-".join(self.id.split("-")[1:])

    @property
    def table(self):
        return get_table(self.id)

    @property
    def exists(self):
        return check_table_exists(self.id)

    @property
    def columns(self):
        return self.table.columns


class SampleTables(BaseModel):
    binning: Optional[AnnotationTable]
    markers: Optional[AnnotationTable]
    metagenome: Optional[AnnotationTable]
    cytoscape: Optional[CytoscapeConnectionsTable]
    # The following are created after user upload
    # via:
    # celery tasks (see tasks.py)
    refinements: Optional[AnnotationTable]
    # geom_medians: Optional[str]

    @property
    def kmers(self) -> List[KmerTable]:
        settings = []
        sizes = [3, 4, 5]
        norm_methods = ["am_clr", "ilr"]
        embed_methods = ["bhsne", "densmap", "umap", "sksne", "trimap"]
        for size, norm_method, embed_method in itertools.product(
            sizes, norm_methods, embed_methods
        ):
            settings.append(
                KmerTable(
                    assembly=self.metagenome,
                    size=size,
                    norm_method=norm_method,
                    embed_dims=2,
                    embed_method=embed_method,
                )
            )
        return settings

    @property
    def embeddings(self) -> List[AnnotationTable]:
        kmer_sizes = set([kmer_table.size for kmer_table in self.kmers])
        norm_methods = set([kmer_table.norm_method for kmer_table in self.kmers])
        # NOTE: The corresponding table-name suffix format (AnnotationTable(id=...))
        # is at https://github.com/WiscEvan/Automappa/blob/977dbbf6dca8cc62f974eb1c6a2f48fc25f2ddb2/automappa/tasks.py#L149
        return [
            AnnotationTable(
                id=self.metagenome.id.replace(
                    "-metagenome", f"-{kmer_size}mers-{norm_method}-embeddings"
                ),
                index_col="contig",
            )
            for kmer_size, norm_method in itertools.product(kmer_sizes, norm_methods)
        ]

    @property
    def marker_symbols(self) -> AnnotationTable:
        return AnnotationTable(
            id=self.markers.id.replace("-markers", "-marker-symbols")
        )

    class Config:
        arbitrary_types_allowed = True
        smart_union = True
