#!/usr/bin/env python

from functools import partial
import uuid
import logging
from pydantic import BaseModel
from typing import List, Optional, Tuple, Union

from dash_extensions.enrich import Serverside

from sqlmodel import Session, select, func

from sqlalchemy.exc import NoResultFound, MultipleResultsFound

from celery import group
from celery.result import GroupResult, AsyncResult
from automappa.data import loader


from automappa.data.database import engine, redis_backend
from automappa.data.models import (
    Metagenome,
    Contig,
    Marker,
    CytoscapeConnection,
)
from automappa.pages.home.tasks.sample_cards import (
    assign_contigs_marker_size,
    assign_contigs_marker_symbol,
    create_metagenome_model,
    initialize_refinement,
)

logger = logging.getLogger(__name__)

MARKER_SET_SIZE = 139


class HomeDataSource(BaseModel):
    async def markers_getter(self, fpath: str) -> List[Marker]:
        await loader.create_markers(fpath)

    async def contigs_getter(
        self, fpath: str, markers: Optional[List[Marker]]
    ) -> List[Contig]:
        await loader.create_contigs(fpath, markers)

    async def metagenome_getter(
        self, fpath: str, contigs: Optional[List[Contig]]
    ) -> Metagenome:
        await loader.create_metagenome(fpath, contigs)

    async def create_sample(
        self, mg_fpath: str, mag_fpath: str, marker_fpath: str
    ) -> int:
        marker_getter = partial(loader.create_markers, marker_fpath)
        contig_getter = partial(loader.create_contigs, mag_fpath)
        contig_getter = partial(contig_getter, markers=await marker_getter())
        metagenome_getter = partial(loader.create_metagenome, mg_fpath)
        metagenome_getter = partial(metagenome_getter, contigs=await contig_getter())
        metagenome = await metagenome_getter()

    def name_is_unique(self, name: str) -> bool:
        """Determine whether metagenome name is unique in the database

        Parameters
        ----------
        name : str
            Name of the metagenome

        Returns
        -------
        bool
            Whether Metagenome.name occurs exactly once in the database
        """
        with Session(engine) as session:
            try:
                session.exec(select(Metagenome).where(Metagenome.name == name)).one()
                is_unique = True
            except NoResultFound:
                is_unique = True
            except MultipleResultsFound:
                is_unique = False
        return is_unique

    def get_metagenome_name(self, metagenome_id: int) -> str:
        with Session(engine) as session:
            name = session.exec(
                select(Metagenome.name).where(Metagenome.id == metagenome_id)
            ).one()
        return name

    def get_metagenome_ids(self) -> List[int]:
        """Get all unique Metagenome names in database

        Returns
        -------
        List[int]
            Metagenome id available in database
        """
        with Session(engine) as session:
            metagenome_ids = session.exec(select(Metagenome.id)).all()
        return metagenome_ids

    def marker_count(self, metagenome_id: int) -> int:
        with Session(engine) as session:
            statement = (
                select([func.count(Marker.id)])
                .join(Contig)
                .join(Metagenome)
                .where(Metagenome.id == metagenome_id)
            )
            marker_count = session.exec(statement).one()
        return marker_count

    def get_approximate_marker_sets(self, metagenome_id: int) -> int:
        marker_count_stmt = (
            select(func.count(Marker.id))
            .join(Contig)
            .where(Contig.metagenome_id == metagenome_id)
        )
        with Session(engine) as session:
            total_markers = session.exec(marker_count_stmt).first()

        return total_markers // MARKER_SET_SIZE

    def contig_count(self, metagenome_id: int) -> int:
        with Session(engine) as session:
            statement = (
                select([func.count(Metagenome.contigs)])
                .join(Contig)
                .where(Metagenome.id == metagenome_id)
            )
            contig_count = session.exec(statement).one()
        return contig_count

    def connections_count(self, metagenome_id: int) -> int:
        with Session(engine) as session:
            statement = (
                select([func.count(Metagenome.connections)])
                .join(CytoscapeConnection)
                .where(Metagenome.id == metagenome_id)
            )
            connection_count = session.exec(statement).first()
        return connection_count

    def validate_uploader_path(
        self,
        is_completed: bool,
        filenames: List[str],
        upload_id: uuid.UUID,
    ) -> str:
        """Given uploader inputs return filepaths in order:

        Tuple[metagenome_fpath, binning_fpath, markers_fpath, connections_fpath]
        """
        fpath = loader.validate_uploader(is_completed, filenames, upload_id)
        if fpath:
            fpath = str(fpath)
        return fpath

    def create_metagenome(
        self,
        name: str,
        metagenome_fpath: str,
        binning_fpath: str,
        markers_fpath: str,
        connections_fpath: Optional[str] = None,
    ) -> Tuple[str, int]:
        logger.info(f"Creating sample {name=}")
        metagenome = loader.create_sample_metagenome(
            name, metagenome_fpath, binning_fpath, markers_fpath, connections_fpath
        )
        loader.create_initial_refinements(metagenome.id)
        return metagenome.name, metagenome.id

    def preprocess_metagenome(
        self,
        name: str,
        metagenome_fpath: str,
        binning_fpath: str,
        markers_fpath: str,
        connections_fpath: Union[str, None] = None,
    ) -> GroupResult:
        task_chain = create_metagenome_model.s() | group(
            [
                assign_contigs_marker_size.s(),
                assign_contigs_marker_symbol.s(),
                initialize_refinement.s(),
            ]
        )
        # NOTE: task ids may be retrieved using .results method
        # (will correspond to order in group)
        # group_result.results: List[AsyncResult]
        result: GroupResult = task_chain.set(countdown=2).delay(
            name=name,
            metagenome_fpath=metagenome_fpath,
            binning_fpath=binning_fpath,
            markers_fpath=markers_fpath,
            connections_fpath=connections_fpath,
        )
        return result

    def get_preprocess_metagenome_tasks(
        self, task_ids: Tuple[str, str, str, str]
    ) -> List[Tuple[str, AsyncResult]]:
        (
            mg_model_task_id,
            marker_size_task_id,
            marker_symbol_task_id,
            refinement_task_id,
        ) = task_ids
        mg_model_task = create_metagenome_model.AsyncResult(mg_model_task_id)
        marker_size_task = assign_contigs_marker_size.AsyncResult(marker_size_task_id)
        marker_symbol_task = assign_contigs_marker_symbol.AsyncResult(
            marker_symbol_task_id
        )
        refinement_task = initialize_refinement.AsyncResult(refinement_task_id)
        return (
            ("ingesting metagenome data", mg_model_task),
            ("pre-computing marker sizes", marker_size_task),
            ("pre-computing marker symbols", marker_symbol_task),
            ("initializing user refinements", refinement_task),
        )
