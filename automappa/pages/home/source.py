#!/usr/bin/env python

from functools import partial
import uuid
import logging
from pydantic import BaseModel
from typing import List, Optional, Tuple, Union

from sqlmodel import Session, select, func

from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from automappa.data import loader


from automappa.data.database import engine
from automappa.data.loader import (
    Metagenome,
    Contig,
    Marker,
    CytoscapeConnection,
)

logger = logging.getLogger(__name__)


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

    def get_sample_names(self) -> List[Tuple[int, str]]:
        """Get all unique Metagenome names in database

        Returns
        -------
        List[str]
            Metagenome names uploaded to/available in database
        """
        with Session(engine) as session:
            sample_names = session.exec(select(Metagenome.id, Metagenome.name)).all()
        return sample_names

    def marker_count(self, metagenome_id: int) -> int:
        with Session(engine) as session:
            statement = (
                select(func.count(Marker.id))
                .join(Contig)
                .join(Metagenome)
                .where(Metagenome.id == metagenome_id)
            )
            marker_count = session.exec(statement).one()
        return marker_count

    def contig_count(self, metagenome_id: int) -> int:
        with Session(engine) as session:
            statement = (
                select(func.count(Metagenome.contigs))
                .join(Contig)
                .where(Metagenome.id == metagenome_id)
            )
            contig_count = session.exec(statement).one()
        return contig_count

    def connections_count(self, metagenome_id: int) -> int:
        with Session(engine) as session:
            statement = (
                select(func.count(Metagenome.connections))
                .join(CytoscapeConnection)
                .where(Metagenome.id == metagenome_id)
            )
            connection_count = session.exec(statement).first()
        return connection_count

    def create_metagenome(
        self,
        name: str,
        metagenome_fpaths: List[str],
        metagenome_is_completed: bool,
        metagenome_upload_id: uuid.UUID,
        binning_fpaths: List[str],
        binning_is_completed: bool,
        binning_upload_id: uuid.UUID,
        markers_fpaths: List[str],
        markers_is_completed: bool,
        markers_upload_id: uuid.UUID,
        connections_fpaths: Union[List[str], None] = None,
        connections_is_completed: Union[bool, None] = None,
        connections_upload_id: Union[uuid.UUID, None] = None,
    ) -> int:
        metagenome_fpath = loader.validate_uploader(
            metagenome_is_completed, metagenome_fpaths, metagenome_upload_id
        )
        binning_fpath = loader.validate_uploader(
            binning_is_completed, binning_fpaths, binning_upload_id
        )
        markers_fpath = loader.validate_uploader(
            markers_is_completed, markers_fpaths, markers_upload_id
        )
        connections_fpath = loader.validate_uploader(
            connections_is_completed, connections_fpaths, connections_upload_id
        )
        logger.info(f"Creating sample {name=}")
        # TODO Create sample should be async so sample_card with loader
        # is displayed and user can continue with navigation
        # TODO Disable "new sample" button while create sample is in progress
        metagenome = loader.create_sample_metagenome(
            name, metagenome_fpath, binning_fpath, markers_fpath, connections_fpath
        )
        return metagenome.id
        # TODO Preprocess marker symbols from marker counts
        # marker_symbols_task = preprocess_marker_symbols.delay(
        #     metagenome_id,
        # )
