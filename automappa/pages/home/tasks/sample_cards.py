#!/usr/bin/env python

from typing import List, Optional, Tuple, Union
from sqlmodel import Session, case, func, select
from automappa.data import loader
from automappa.data.database import engine
from automappa.data.models import Contig, Marker
from automappa.tasks import queue


@queue.task(bind=True)
def create_metagenome(
    self,
    name: str,
    metagenome_fpath: str,
    binning_fpath: str,
    markers_fpath: str,
    connections_fpath: Union[List[str], None] = None,
) -> Tuple[str, int]:
    # TODO Create sample should be async so sample_card with loader
    # is displayed and user can continue with navigation
    # TODO Disable "new sample" button while create sample is in progress
    metagenome = loader.create_sample_metagenome(
        name, metagenome_fpath, binning_fpath, markers_fpath, connections_fpath
    )
    loader.create_initial_refinements(metagenome.id)
    return metagenome.name, metagenome.id


@queue.task(bind=True)
def create_metagenome_model(
    self,
    name: str,
    metagenome_fpath: str,
    binning_fpath: str,
    markers_fpath: str,
    connections_fpath: Optional[str] = None,
) -> int:
    metagenome = loader.create_sample_metagenome(
        name, metagenome_fpath, binning_fpath, markers_fpath, connections_fpath
    )
    return metagenome.id


@queue.task(bind=True)
def initialize_refinement(self, metagenome_id: int) -> None:
    loader.create_initial_refinements(metagenome_id)


@queue.task(bind=True)
def assign_contigs_marker_symbol(self, metagenome_id: int) -> None:
    subquery = (
        select(
            [
                Contig.id,
                case(
                    [
                        (func.count(Marker.id) == 0, "circle"),
                        (func.count(Marker.id) == 1, "square"),
                        (func.count(Marker.id) == 2, "diamond"),
                        (func.count(Marker.id) == 3, "triangle-up"),
                        (func.count(Marker.id) == 4, "x"),
                        (func.count(Marker.id) == 5, "pentagon"),
                        (func.count(Marker.id) == 6, "hexagon2"),
                        (func.count(Marker.id) >= 7, "hexagram"),
                    ],
                    else_="circle",
                ).label("symbol"),
            ]
        )
        .select_from(Contig)
        .join(Marker, isouter=True)
        .group_by(Contig.id)
        .subquery()
    )
    stmt = (
        select(Contig, subquery.c.symbol)
        .select_from(Contig)
        .join(subquery, subquery.c.id == Contig.id)
    )
    stmt = stmt.where(Contig.metagenome_id == metagenome_id)
    with Session(engine) as session:
        results = session.exec(stmt).all()
        for contig, symbol in results:
            contig.marker_symbol = symbol
            session.add(contig)

        session.commit()


@queue.task(bind=True)
def assign_contigs_marker_size(self, metagenome_id: int) -> None:
    subquery = (
        select(
            [
                Contig.id,
                case(
                    [
                        (func.count(Marker.id) == 0, 7),
                        (func.count(Marker.id) == 1, 8),
                        (func.count(Marker.id) == 2, 9),
                        (func.count(Marker.id) == 3, 10),
                        (func.count(Marker.id) == 4, 11),
                        (func.count(Marker.id) == 5, 12),
                        (func.count(Marker.id) == 6, 13),
                        (func.count(Marker.id) >= 7, 14),
                    ],
                    else_=7,
                ).label("size"),
            ]
        )
        .select_from(Contig)
        .join(Marker, isouter=True)
        .group_by(Contig.id)
        .subquery()
    )
    stmt = (
        select(Contig, subquery.c.size)
        .select_from(Contig)
        .join(subquery, subquery.c.id == Contig.id)
    )
    stmt = stmt.where(Contig.metagenome_id == metagenome_id)
    with Session(engine) as session:
        results = session.exec(stmt).all()
        for contig, size in results:
            contig.marker_size = size
            session.add(contig)

        session.commit()
