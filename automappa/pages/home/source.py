#!/usr/bin/env python

from functools import partial
import uuid
import logging
from pydantic import BaseModel
from typing import List, Optional, Tuple, Union

from sqlmodel import Session, and_, select, func

from sqlalchemy.exc import NoResultFound, MultipleResultsFound

from celery import group
from celery.result import GroupResult, AsyncResult
from automappa.data import loader


from automappa.data.database import engine
from automappa.data.models import (
    Metagenome,
    Contig,
    Marker,
    CytoscapeConnection,
    Refinement,
)
from automappa.pages.home.tasks.sample_cards import (
    assign_contigs_marker_size,
    assign_contigs_marker_symbol,
    create_metagenome_model,
    initialize_refinement,
)

logger = logging.getLogger(__name__)

MARKER_SET_SIZE = 139
HIGH_QUALITY_COMPLETENESS = 90  # gt
HIGH_QUALITY_PURITY = 95  # gt
MEDIUM_QUALITY_COMPLETENESS = 50  # gte
MEDIUM_QUALITY_PURITY = 90  # gt
# lt
LOW_QUALITY_COMPLETENESS = 50
LOW_QUALITY_PURITY = 90


class HomeDataSource(BaseModel):
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

    def remove_metagenome(self, metagenome_id: int) -> None:
        with Session(engine) as session:
            metagenome = session.exec(
                select(Metagenome).where(Metagenome.id == metagenome_id)
            ).one()
            session.delete(metagenome)
            session.commit()

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

    def get_refined_contig_count(self, metagenome_id: int) -> int:
        stmt = (
            select(func.count(Contig.id))
            .where(Contig.metagenome_id == metagenome_id)
            .where(Contig.refinements.any(Refinement.outdated == False))
        )
        with Session(engine) as session:
            count = session.exec(stmt).first() or 0
        return count

    def get_refinements_count(
        self,
        metagenome_id: int,
        initial: Optional[bool] = None,
        outdated: Optional[bool] = None,
    ) -> int:
        """Get Refinement count where Refinement.metagenome_id == metagenome_id

        Providing `initial` will add where(Refinement.initial_refinement == True)
        otherwise will omit this filter and retrieve all.
        """
        stmt = select(func.count(Refinement.id)).where(
            Refinement.metagenome_id == metagenome_id
        )
        if isinstance(initial, bool):
            stmt = stmt.where(Refinement.initial_refinement == initial)
        if isinstance(outdated, bool):
            stmt = stmt.where(Refinement.outdated == outdated)
        with Session(engine) as session:
            count = session.exec(stmt).first() or 0
        return count

    def compute_completeness_purity_metrics(
        self, metagenome_id: int, refinement_id: int
    ) -> Tuple[float, float]:
        marker_count_stmt = (
            select(func.count(Marker.id))
            .join(Contig)
            .where(
                Contig.metagenome_id == metagenome_id,
                Contig.refinements.any(
                    and_(
                        Refinement.outdated == False,
                        Refinement.id == refinement_id,
                    )
                ),
            )
        )
        unique_marker_stmt = (
            select(Marker.sacc)
            .join(Contig)
            .distinct()
            .where(
                Contig.metagenome_id == metagenome_id,
                Contig.refinements.any(
                    and_(
                        Refinement.outdated == False,
                        Refinement.id == refinement_id,
                    )
                ),
            )
        )
        with Session(engine) as session:
            markers_count = session.exec(marker_count_stmt).first() or 0
            unique_marker_count = session.exec(
                select(func.count()).select_from(unique_marker_stmt)
            ).first()

        completeness = round(unique_marker_count / MARKER_SET_SIZE * 100, 2)
        purity = (
            round(unique_marker_count / markers_count * 100, 2) if markers_count else 0
        )
        return completeness, purity

    def get_mimag_counts(self, metagenome_id: int) -> Tuple[int, int, int]:
        """Retrieve counts of clusters following MIMAG standards.

        standards:

        - High-quality >90% complete > 95% pure
        - Medium-quality >=50% complete > 90% pure
        - Low-quality <50% complete < 90% pure

        """
        stmt = select(Refinement.id).where(
            Refinement.metagenome_id == metagenome_id,
            Refinement.outdated == False,
        )
        high_quality_count = 0
        medium_quality_count = 0
        low_quality_count = 0
        with Session(engine) as session:
            refinement_ids = session.exec(stmt).all()
            for refinement_id in refinement_ids:
                completeness, purity = self.compute_completeness_purity_metrics(
                    metagenome_id, refinement_id
                )
                if (
                    completeness > HIGH_QUALITY_COMPLETENESS
                    and purity > HIGH_QUALITY_PURITY
                ):
                    high_quality_count += 1
                elif (
                    completeness >= MEDIUM_QUALITY_COMPLETENESS
                    and purity > MEDIUM_QUALITY_PURITY
                ):
                    medium_quality_count += 1
                else:
                    # completeness < LOW_QUALITY_COMPLETENESS and purity < LOW_QUALITY_PURITY:
                    low_quality_count += 1
        return high_quality_count, medium_quality_count, low_quality_count
