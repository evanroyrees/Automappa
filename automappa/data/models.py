#!/usr/bin/env python
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


class Metagenome(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    contigs: List["Contig"] = Relationship(back_populates="metagenome")
    refinements: List["Refinement"] = Relationship(back_populates="metagenome")
    connections: List["CytoscapeConnection"] = Relationship(back_populates="metagenome")


class ContigRefinementLink(SQLModel, table=True):
    refinement_id: Optional[int] = Field(
        default=None, foreign_key="refinement.id", primary_key=True
    )
    contig_id: Optional[int] = Field(
        default=None, foreign_key="contig.id", primary_key=True
    )


class Refinement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default=utc_now())
    contigs: List["Contig"] = Relationship(
        back_populates="refinements", link_model=ContigRefinementLink
    )
    metagenome_id: Optional[int] = Field(default=None, foreign_key="metagenome.id")
    metagenome: Optional[Metagenome] = Relationship(back_populates="refinements")


class Contig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    header: str = Field(index=True)
    seq: Optional[str]
    cluster: Optional[str] = Field(index=True)
    completeness: Optional[float]
    purity: Optional[float]
    coverage_stddev: Optional[float]
    gc_content_stddev: Optional[float]
    coverage: Optional[float] = Field(index=True)
    gc_content: Optional[float]
    length: Optional[int]
    superkingdom: Optional[str]
    phylum: Optional[str]
    klass: Optional[str]
    order: Optional[str]
    family: Optional[str]
    genus: Optional[str]
    species: Optional[str]
    taxid: Optional[int]
    x_1: Optional[float]
    x_2: Optional[float]
    marker_symbol: Optional[str]
    marker_size: Optional[int]
    refinements: Optional[List[Refinement]] = Relationship(
        back_populates="contigs", link_model=ContigRefinementLink
    )
    metagenome_id: Optional[int] = Field(default=None, foreign_key="metagenome.id")
    metagenome: Optional[Metagenome] = Relationship(back_populates="contigs")
    markers: Optional[List["Marker"]] = Relationship(back_populates="contig")


class Marker(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    orf: str  # qname
    sacc: str
    sname: str
    full_seq_score: float = Field(index=True)
    cutoff: float = Field(index=True)
    contig_id: Optional[int] = Field(default=None, foreign_key="contig.id")
    contig: Contig = Relationship(back_populates="markers")


class CytoscapeConnection(SQLModel, table=True):
    __tablename__ = "cytoscape_connection"
    id: Optional[int] = Field(default=None, primary_key=True)
    node1: str
    interaction: int
    node2: str
    connections: int
    mappingtype: str  # Literal["intra", "ss", "se", "ee"]
    name: Optional[str]
    contiglength: Optional[int]
    metagenome_id: Optional[int] = Field(default=None, foreign_key="metagenome.id")
    metagenome: Optional[Metagenome] = Relationship(back_populates="connections")
