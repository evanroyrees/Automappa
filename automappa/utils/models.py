from pydantic import BaseModel, Field, PydanticValueError, create_model
from pydantic.fields import ModelField
from typing import List, Literal, Optional
# from cached_property import cached_property_with_ttl
from celery.result import AsyncResult

from automappa.db import engine,metadata
from automappa.utils.serializers import get_table

class RestrictedAlphabetStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value, field: ModelField):
        alphabet = field.field_info.extra['alphabet']
        if any(c not in alphabet for c in value):
            raise ValueError(f'{value!r} is not restricted to {alphabet!r}')
        return cls(value)

    @classmethod
    def __modify_schema__(cls, field_schema, field: Optional[ModelField]):
        if field:
            alphabet = field.field_info.extra['alphabet']
            field_schema['examples'] = [c * 4 for c in alphabet]

class MetagenomeAnnotations(BaseModel):
    contig: str
    binning: Optional[str]
    refinements: Optional[str]
    markers: Optional[str]
    # marker_symbols: Union[AsyncResult,str]
    metagenome: Optional[str]


class NotInDatabaseError(PydanticValueError):
    code = 'table_name_not_in_db'
    tables = metadata.tables.keys()
    msg_template = f'value "TEMPLATE" is not in {tables}'
    msg_template = msg_template.replace("TEMPLATE", "{table_name}")


class AnnotationTable(BaseModel):
    id: str
    index_col: Optional[str] = "contig"

    # @validator('id', pre=True)
    # @validator('id')
    # def table_must_exist_in_database(cls, v):
    #     if v not in metadata.tables.keys():
    #         # if not engine.has_table(v):
    #         raise NotInDatabaseError(table_name=v)
    #     return v

    # @validator('index_col')
    # def index_col_in_table(cls, v, values):
    #     table_id = values.get('id')
    #     table_cols = get_table(table_id).columns
    #     if v not in table_cols:
    #         raise ValueError(f'{v} not in {table_id} columns {table_cols}')
    #     return v

    # class Config:
    #     keep_untouched=(cached_property,)


    @property
    def sample(self):
        return self.id.split('-')[0]
    
    @property
    def name(self):
        return '-'.join(self.id.split('-')[1:])

    @property
    def table(self):
        return get_table(self.id, index_col=self.index_col)
    
    @property
    def exists(self):
        return engine.has_table(self.id)

    @property
    def columns(self):
        return self.table.columns

# class ResultTable(AnnotationTable):
#     task: Optional[AsyncResult]
    
#     @cached_property_with_ttl(60) # cache invalidates after 60 sec
#     def table(self):
#         return get_table(self.id, index_col=self.index_col)

#     class Config:
#         arbitrary_types_allowed = True
#         smart_union = True
class KmerTable(BaseModel):
    assembly: AnnotationTable
    size: Literal[3, 4, 5] = 5
    norm_method: Literal["am_clr", "ilr", "clr"] = "am_clr"
    embed_dims: Optional[int] = 2
    embed_method: Literal["bhsne", "sksne", "umap", "densmap", "trimap"] = "bhsne"

    @property
    def counts(self) -> AnnotationTable:
        return AnnotationTable(id=self.assembly.id.replace("-metagenome", f"-{self.size}mers"))
    
    @property
    def norm_freqs(self) -> AnnotationTable:
        return AnnotationTable(id=self.assembly.id.replace("-metagenome", f"-{self.size}mers-{self.norm_method}"))
    
    @property
    def embedding(self) -> AnnotationTable:
        return AnnotationTable(id=self.assembly.id.replace("-metagenome", f"-{self.size}mers-{self.norm_method}-{self.embed_method}"))

class SampleTables(BaseModel):
    binning: Optional[AnnotationTable]
    markers: Optional[AnnotationTable]
    metagenome: Optional[AnnotationTable]
    # The following are created after user upload
    # via: 
    # db ingestion (see serializers.py)
    # celery tasks (see tasks.py)
    refinements: Optional[AnnotationTable]
    # geom_medians: Optional[str]

    @property
    def kmers(self) -> List[KmerTable]:
        settings = []
        for size in [3,4,5]:
            for norm_method in ["am_clr"]:
                for embed_method in ["bhsne", "densmap", "umap", "sksne", "trimap"]:
                    settings.append(KmerTable(
                        assembly=self.metagenome,
                        size=size,
                        norm_method=norm_method,
                        embed_dims=2,
                        embed_method=embed_method,
                    ))
        return settings
            
    @property
    def embeddings(self) -> AnnotationTable:
        return AnnotationTable(id=self.metagenome.id.replace("-metagenome","-embeddings"))

    @property
    def marker_symbols(self) -> AnnotationTable:
        return AnnotationTable(id=self.markers.id.replace('-markers','-marker-symbols'))
    
    # embeddings: Union[AsyncResult,str]
   
    # validators
    # @validator('*')
    # def table_must_exist_in_database(cls, v):
    #     if not engine.has_table(v):
    #         raise NotInDatabaseError(table_name=v)
    #     return v

    # Generic Class Methods
    # e.g. tables.binning.get_table()
    # or tables.binning.exists()
    # or tables.binning.tasks()
    # etc.
    # Need generic methods (listed above) to apply from namespace

    class Config:
        arbitrary_types_allowed = True
        smart_union = True
    


MarkerAnnotations = create_model(
    'MarkerAnnotations',
    apple='russet',
    banana='yellow',
    __base__=MetagenomeAnnotations,
)

class TaxonomyAnnotations(MetagenomeAnnotations):
    taxid: int
    superkingdom: Optional[str]
    phylum: Optional[str]
    klass: Optional[str]
    order: Optional[str]
    family: Optional[str]
    genus: Optional[str]
    species: Optional[str]
    
class CoverageAnnotations(MetagenomeAnnotations):
    coverage: float

class KmerAnnotations(MetagenomeAnnotations):
    x_1: float
    x_2: float
    kmer_size: Optional[int]
    norm_method: Optional[str]
    embed_method: Optional[str]

class Kmer(BaseModel):
    value: RestrictedAlphabetStr = Field(alphabet='ATCG')

class KmerCounts(MetagenomeAnnotations):
    # kmers: Field(..., regex = 'ATCG')
    kmers: List[Kmer]

class BinningAnnotations(MetagenomeAnnotations):
    cluster: str
    completeness: Optional[float]
    purity: Optional[float]
    gc_stddev: Optional[float]
    coverage_stddev: Optional[float]


class MetagenomeModel(BaseModel):
    # Json
    contig: str
    gc_content: Optional[float]
    length: Optional[int]
    markers: Optional[MarkerAnnotations]
    kmers: Optional[KmerAnnotations]
    binning: Optional[BinningAnnotations]
    coverage: Optional[CoverageAnnotations]
    taxonomy: Optional[TaxonomyAnnotations]
