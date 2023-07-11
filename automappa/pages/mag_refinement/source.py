#!/usr/bin/env python


import itertools
import logging
import pandas as pd
from pydantic import BaseModel
from typing import Dict, List, Literal, Optional, Set, Tuple, Union

from sqlmodel import Session, and_, or_, select, func, case

from automappa.data.database import engine
from automappa.data.loader import Metagenome, Contig, Marker
from automappa.data.models import CytoscapeConnection, Refinement
from automappa.data.schemas import ContigSchema
from automappa.data.source import sqlmodel_to_df
from datetime import datetime

logger = logging.getLogger(__name__)


class RefinementDataSource(BaseModel):
    def get_sankey_records(
        self,
        metagenome_id: int,
        headers: Optional[List[str]],
        selected_rank: Literal[
            "superkingdom", "phylum", "class", "order", "family", "genus", "species"
        ] = ContigSchema.SPECIES,
    ) -> pd.DataFrame:
        ranks = [
            "superkingdom",
            "phylum",
            "class",
            "order",
            "family",
            "genus",
            "species",
        ]
        ranks = ranks[: ranks.index(selected_rank) + 1]
        model_ranks = {
            "superkingdom": Contig.superkingdom,
            "phylum": Contig.phylum,
            "class": Contig.klass,
            "order": Contig.order,
            "family": Contig.family,
            "genus": Contig.genus,
            "species": Contig.species,
        }
        selections = [model_ranks.get(rank) for rank in ranks]
        selections.insert(0, Contig.header)
        with Session(engine) as session:
            statement = (
                select(*selections)
                .join(Metagenome)
                .where(Metagenome.id == metagenome_id)
            )
            if headers:
                statement = statement.where(Contig.header.in_(headers))
            results = session.exec(statement).all()

        schema_ranks = {
            "superkingdom": ContigSchema.DOMAIN,
            "phylum": ContigSchema.PHYLUM,
            "class": ContigSchema.CLASS,
            "order": ContigSchema.ORDER,
            "family": ContigSchema.FAMILY,
            "genus": ContigSchema.GENUS,
            "species": ContigSchema.SPECIES,
        }
        columns = [schema_ranks[rank] for rank in ranks]
        columns.insert(0, ContigSchema.HEADER)

        df = pd.DataFrame.from_records(
            results,
            index=ContigSchema.HEADER,
            columns=columns,
        ).fillna("unclassified")

        for rank in df.columns:
            df[rank] = df[rank].map(lambda taxon: f"{rank[0]}_{taxon}")

        return df

    def get_coverage_boxplot_records(
        self, metagenome_id: int, headers: List[str]
    ) -> pd.DataFrame:
        with Session(engine) as session:
            statement = select(Contig).where(Contig.metagenome_id == metagenome_id)
            if headers:
                statement = statement.where(Contig.header.in_(headers))
            results = session.exec(statement).all()
        return sqlmodel_to_df(results)

    def get_coverage_min_max_values(self, metagenome_id: int) -> Tuple[float, float]:
        with Session(engine) as session:
            statement = select(
                func.min(Contig.coverage), func.max(Contig.coverage)
            ).where(Contig.metagenome_id == metagenome_id)
            min_cov, max_cov = session.exec(statement).first()
        return min_cov, max_cov

    def get_contig_headers_from_coverage_range(
        self, metagenome_id: int, coverage_range: Tuple[float, float]
    ) -> Set[str]:
        min_cov, max_cov = coverage_range
        with Session(engine) as session:
            headers = session.exec(
                select([Contig.header]).where(
                    Contig.metagenome_id == metagenome_id,
                    Contig.coverage >= min_cov,
                    Contig.coverage <= max_cov,
                )
            ).all()
        return set(headers)

    def get_refinement_contig_headers(self, metagenome_id: int) -> Set[str]:
        stmt = select(Contig.header).where(
            Contig.metagenome_id == metagenome_id,
            Contig.refinements.any(
                and_(
                    Refinement.initial_refinement == False,
                    Refinement.outdated == False,
                )
            ),
        )
        with Session(engine) as session:
            headers = session.exec(stmt).all()
        return set(headers)

    def get_scatterplot2d_records(
        self,
        metagenome_id: int,
        x_axis: str,
        y_axis: str,
        color_by_col: str,
        headers: Optional[List[str]] = [],
    ) -> Dict[
        Literal["x", "y", "marker_symbol", "marker_size", "text", "customdata"],
        List[Union[float, str, Tuple[float, float, int]]],
    ]:
        axes = {
            ContigSchema.LENGTH: Contig.length,
            ContigSchema.COVERAGE: Contig.coverage,
            ContigSchema.GC_CONTENT: Contig.gc_content,
            ContigSchema.X_1: Contig.x_1,
            ContigSchema.X_2: Contig.x_2,
        }
        # Set color by column
        categoricals = {
            ContigSchema.CLUSTER: Contig.cluster,
            ContigSchema.SUPERKINGDOM: Contig.superkingdom,
            ContigSchema.PHYLUM: Contig.phylum,
            ContigSchema.CLASS: Contig.klass,
            ContigSchema.ORDER: Contig.order,
            ContigSchema.FAMILY: Contig.family,
            ContigSchema.GENUS: Contig.genus,
            ContigSchema.SPECIES: Contig.species,
        }

        name_select = categoricals[color_by_col]
        x_select = axes[x_axis]
        y_select = axes[y_axis]

        marker_symbols_subquery = (
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
            select(
                x_select,
                y_select,
                marker_symbols_subquery.c.size,
                marker_symbols_subquery.c.symbol,
                Contig.coverage,
                Contig.gc_content,
                Contig.length,
                Contig.header,
                name_select,
            )
            .select_from(Contig)
            .join(
                marker_symbols_subquery,
                marker_symbols_subquery.c.id == Contig.id,
            )
        )

        if headers:
            stmt = stmt.where(Contig.header.in_(headers))

        stmt = stmt.where(Contig.metagenome_id == metagenome_id)

        # query db
        with Session(engine) as session:
            results = session.exec(stmt).all()

        # format for traces
        data = {}
        for (
            x,
            y,
            marker_size,
            marker_symbol,
            coverage,
            gc_content,
            length,
            header,
            name,
        ) in results:
            customdata = (coverage, gc_content, length)
            if name not in data:
                data[name] = dict(
                    x=[x],
                    y=[y],
                    marker_size=[marker_size],
                    marker_symbol=[marker_symbol],
                    customdata=[customdata],
                    text=[header],
                )
            else:
                data[name]["x"].append(x)
                data[name]["y"].append(y)
                data[name]["marker_size"].append(marker_size)
                data[name]["marker_symbol"].append(marker_symbol)
                data[name]["customdata"].append(customdata)
                data[name]["text"].append(header)
        return data

    def get_scaterplot3d_records(
        self,
        metagenome_id: int,
        x_axis: str,
        y_axis: str,
        z_axis: str,
        color_by_col: str,
        headers: Optional[List[str]] = [],
    ) -> Dict[
        str,
        Dict[Literal["x", "y", "z", "marker_size", "text"], List[Union[float, str]]],
    ]:
        # Set x,y,z axes
        axes = {
            ContigSchema.LENGTH: Contig.length,
            ContigSchema.COVERAGE: Contig.coverage,
            ContigSchema.GC_CONTENT: Contig.gc_content,
            ContigSchema.X_1: Contig.x_1,
            ContigSchema.X_2: Contig.x_2,
        }
        # Set color by column
        categoricals = {
            ContigSchema.CLUSTER: Contig.cluster,
            ContigSchema.SUPERKINGDOM: Contig.superkingdom,
            ContigSchema.PHYLUM: Contig.phylum,
            ContigSchema.CLASS: Contig.klass,
            ContigSchema.ORDER: Contig.order,
            ContigSchema.FAMILY: Contig.family,
            ContigSchema.GENUS: Contig.genus,
            ContigSchema.SPECIES: Contig.species,
        }
        name_select = categoricals[color_by_col]
        x_select = axes[x_axis]
        y_select = axes[y_axis]
        z_select = axes[z_axis]
        stmt = select(
            x_select,
            y_select,
            z_select,
            (
                (
                    func.ceil(
                        (Contig.length - func.min(Contig.length).over())
                        / (
                            func.max(Contig.length).over()
                            - func.min(Contig.length).over()
                        )
                    )
                    * 2
                    + 4
                ).label("marker_size")
            ),
            Contig.header,
            name_select,
        )

        if headers:
            stmt = stmt.where(Contig.header.in_(headers))

        stmt = stmt.where(Contig.metagenome_id == metagenome_id)
        with Session(engine) as session:
            results = session.exec(stmt).all()

        data = {}
        for x, y, z, marker_size, header, name in results:
            if name not in data:
                data[name] = dict(
                    x=[x], y=[y], z=[z], marker_size=[marker_size], text=[header]
                )
            else:
                data[name]["x"].append(x)
                data[name]["y"].append(y)
                data[name]["z"].append(z)
                data[name]["marker_size"].append(marker_size)
                data[name]["text"].append(header)
        return data

    def get_color_by_column_options(self) -> List[Dict[Literal["label", "value"], str]]:
        categoricals = [
            ContigSchema.CLUSTER,
            ContigSchema.SUPERKINGDOM,
            ContigSchema.PHYLUM,
            ContigSchema.CLASS,
            ContigSchema.ORDER,
            ContigSchema.FAMILY,
            ContigSchema.GENUS,
            ContigSchema.SPECIES,
        ]
        return [
            {"label": category.title(), "value": category} for category in categoricals
        ]

    def get_scatterplot_2d_axes_options(
        self,
    ) -> List[Dict[Literal["label", "value", "disabled"], str]]:
        axes = {
            ContigSchema.LENGTH,
            ContigSchema.COVERAGE,
            ContigSchema.GC_CONTENT,
            ContigSchema.X_1,
            ContigSchema.X_2,
        }
        axes_permutations = itertools.permutations(axes, 2)
        options = []
        for x_axis, y_axis in axes_permutations:
            x_axis_label = (
                "GC content" if ContigSchema.GC_CONTENT in x_axis else x_axis.title()
            )
            y_axis_label = (
                "GC content" if ContigSchema.GC_CONTENT in y_axis else y_axis.title()
            )
            label = f"{x_axis_label} vs. {y_axis_label}"
            value = "|".join([x_axis, y_axis])
            options.append({"label": label, "value": value})

        return options

    def get_scatterplot_3d_zaxis_dropdown_options(
        self,
    ) -> List[Dict[Literal["label", "value", "disabled"], str]]:
        axes = {
            ContigSchema.LENGTH,
            ContigSchema.COVERAGE,
            ContigSchema.GC_CONTENT,
        }
        options = []
        for value in axes:
            label = "GC content" if ContigSchema.GC_CONTENT in value else value.title()
            options.append({"label": label, "value": value})

        return options

    def get_taxonomy_distribution_dropdown_options(
        self,
    ) -> List[Dict[Literal["label", "value"], str]]:
        ranks = [
            ContigSchema.CLASS,
            ContigSchema.ORDER,
            ContigSchema.FAMILY,
            ContigSchema.GENUS,
            ContigSchema.SPECIES,
        ]
        return [{"label": rank.title(), "value": rank} for rank in ranks]

    def update_refinements(self, metagenome_id: int, headers: List[str]) -> None:
        with Session(engine) as session:
            results = session.exec(
                select(Contig)
                .where(Contig.metagenome_id == metagenome_id)
                .where(Contig.header.in_(headers))
            ).all()
        bin_df = sqlmodel_to_df(results, set_index=False).drop(columns=["id"])
        # TODO Add Refinement model associated with metagenome
        # FIXME
        # Allow arbitrary updates to Contig binning where initial data is not touched
        refinement_cols = [col for col in bin_df.columns if "refinement" in col]
        refinement_num = len(refinement_cols) + 1
        refinement_name = f"refinement_{refinement_num}"
        bin_df.loc[headers, refinement_name] = refinement_name
        bin_df = bin_df.fillna(axis="columns", method="ffill")
        bin_df.reset_index(inplace=True)
        # table_to_db(df=bin_df, name=sample.refinements.id)

    def get_marker_overview(
        self, metagenome_id: int
    ) -> List[Dict[Literal["metric", "metric_value"], Union[str, int, float]]]:
        MARKER_SET_SIZE = 139
        marker_count_stmt = (
            select(func.count(Marker.id))
            .join(Contig)
            .where(Contig.metagenome_id == metagenome_id)
        )
        with Session(engine) as session:
            total_markers = session.exec(marker_count_stmt).first()

        markers_sets = total_markers // MARKER_SET_SIZE
        return [
            {"metric": "Total Markers", "metric_value": total_markers},
            {"metric": "Marker Set Size", "metric_value": MARKER_SET_SIZE},
            {"metric": "Approx. Marker Sets", "metric_value": markers_sets},
        ]

    def get_mag_metrics(
        self, metagenome_id: int, headers: Optional[List[str]]
    ) -> List[Dict[Literal["metric", "metric_value"], Union[str, int, float]]]:
        MARKER_SET_SIZE = 139
        contig_count_stmt = select(func.count(Contig.id)).where(
            Contig.metagenome_id == metagenome_id
        )
        marker_contig_count_stmt = (
            select(func.count(func.distinct(Marker.contig_id)))
            .join(Contig)
            .where(Contig.metagenome_id == metagenome_id)
        )
        # - single-copy marker contig count
        single_copy_stmt = (
            select(Contig.id)
            .where(Contig.metagenome_id == metagenome_id)
            .join(Marker)
            .group_by(Contig.id)
            .having(func.count(Marker.id) == 1)
        )
        # - multi-copy marker contig count
        multi_copy_stmt = (
            select(Contig.id)
            .where(Contig.metagenome_id == metagenome_id)
            .join(Marker)
            .group_by(Contig.id)
            .having(func.count(Marker.id) > 1)
        )
        marker_count_stmt = (
            select(func.count(Marker.id))
            .join(Contig)
            .where(Contig.metagenome_id == metagenome_id)
        )
        unique_marker_stmt = (
            select(Marker.sacc)
            .join(Contig)
            .distinct()
            .where(Contig.metagenome_id == metagenome_id)
        )
        redundant_marker_sacc_stmt = (
            select(Marker.sacc)
            .join(Contig)
            .where(Contig.metagenome_id == metagenome_id)
            .group_by(Marker.sacc)
            .having(func.count(Marker.id) > 1)
        )
        if headers:
            contig_count_stmt = contig_count_stmt.where(Contig.header.in_(headers))
            marker_contig_count_stmt = marker_contig_count_stmt.where(
                Contig.header.in_(headers)
            )
            multi_copy_stmt = multi_copy_stmt.where(Contig.header.in_(headers))
            single_copy_stmt = single_copy_stmt.where(Contig.header.in_(headers))
            redundant_marker_sacc_stmt = redundant_marker_sacc_stmt.where(
                Contig.header.in_(headers)
            )
            marker_count_stmt = marker_count_stmt.where(Contig.header.in_(headers))
            unique_marker_stmt = unique_marker_stmt.where(Contig.header.in_(headers))

        with Session(engine) as session:
            contig_count = session.exec(contig_count_stmt).first() or 0
            marker_contigs_count = session.exec(marker_contig_count_stmt).first() or 0
            single_copy_contig_count = (
                session.exec(select(func.count()).select_from(single_copy_stmt)).first()
                or 0
            )
            multi_copy_contig_count = (
                session.exec(select(func.count()).select_from(multi_copy_stmt)).first()
                or 0
            )
            markers_count = session.exec(marker_count_stmt).first() or 0
            unique_marker_count = session.exec(
                select(func.count()).select_from(unique_marker_stmt)
            ).first()
            redundant_marker_sacc = session.exec(redundant_marker_sacc_stmt).all()

        completeness = round(unique_marker_count / MARKER_SET_SIZE * 100, 2)
        purity = (
            round(unique_marker_count / markers_count * 100, 2) if markers_count else 0
        )

        row_data = [
            {"metric": "Contigs", "metric_value": contig_count},
            {
                "metric": "Marker Contigs",
                "metric_value": marker_contigs_count,
            },
            {
                "metric": "Multi-Marker Contigs",
                "metric_value": multi_copy_contig_count,  # Forcepia sp. should be 968
            },
            {
                "metric": "Single-Marker Contigs",
                "metric_value": single_copy_contig_count,  # Forcepia sp. should be 1321
            },
            {"metric": "Markers Count", "metric_value": markers_count},
            {
                "metric": "Redundant Markers",
                "metric_value": len(redundant_marker_sacc),
            },
            {
                "metric": "Redundant Marker Accessions",
                "metric_value": ", ".join(redundant_marker_sacc),
            },
        ]
        if headers:
            row_data.insert(0, {"metric": "Purity (%)", "metric_value": purity})
            row_data.insert(
                0, {"metric": "Completeness (%)", "metric_value": completeness}
            )
        return row_data

    def get_coverage_boxplot_records(
        self, metagenome_id: int, headers: Optional[List[str]]
    ) -> List[Tuple[str, pd.Series]]:
        with Session(engine) as session:
            stmt = select(Contig.coverage).where(Contig.metagenome_id == metagenome_id)
            if headers:
                stmt = stmt.where(Contig.header.in_(headers))
            coverages = session.exec(stmt).all()
        return [
            (
                ContigSchema.COVERAGE.title(),
                pd.Series(coverages, name=ContigSchema.COVERAGE).round(2),
            )
        ]

    def get_gc_content_boxplot_records(
        self, metagenome_id: int, headers: Optional[List[str]]
    ) -> List[Tuple[str, pd.Series]]:
        with Session(engine) as session:
            stmt = select(Contig.gc_content).where(
                Contig.metagenome_id == metagenome_id
            )
            if headers:
                stmt = stmt.where(Contig.header.in_(headers))
            gc_contents = session.exec(stmt).all()

        return [
            (
                "GC Content",
                pd.Series(gc_contents, name=ContigSchema.GC_CONTENT).round(2),
            )
        ]

    def get_length_boxplot_records(
        self, metagenome_id: int, headers: Optional[List[str]]
    ) -> List[Tuple[str, pd.Series]]:
        with Session(engine) as session:
            stmt = select(Contig.length).where(Contig.metagenome_id == metagenome_id)
            if headers:
                stmt = stmt.where(Contig.header.in_(headers))
            lengths = session.exec(stmt).all()
        return [(ContigSchema.LENGTH.title(), pd.Series(lengths))]

    def get_cytoscape_elements(
        self, metagenome_id: int, headers: Optional[List[str]] = []
    ) -> List[
        Dict[
            Literal["data"],
            Dict[
                Literal["id", "label", "source", "target", "connections"],
                Union[str, int],
            ],
        ]
    ]:
        stmt = (
            select(
                CytoscapeConnection.node1,
                CytoscapeConnection.node2,
                CytoscapeConnection.connections,
            )
            .select_from(CytoscapeConnection)
            .where(CytoscapeConnection.metagenome_id == metagenome_id)
        )
        if headers:
            start_nodes = {f"{header}s" for header in headers}
            end_nodes = {f"{header}e" for header in headers}
            nodes = start_nodes.union(end_nodes)
            stmt = stmt.where(
                or_(
                    CytoscapeConnection.node1.in_(nodes),
                    CytoscapeConnection.node2.in_(nodes),
                )
            )
        with Session(engine) as session:
            records = session.exec(stmt).all()

        src_nodes = {src_node for src_node, *_ in records}
        target_nodes = {target_node for _, target_node, _ in records}
        nodes = [
            dict(data=dict(id=node, label=node))
            for node in src_nodes.union(target_nodes)
        ]
        edges = [
            dict(
                data=dict(source=src_node, target=target_node, connections=connections)
            )
            for src_node, target_node, connections in records
        ]
        return nodes + edges

    def get_cytoscape_stylesheet(
        self, metagenome_id: int, headers: Optional[List[str]]
    ) -> List:
        stmt = (
            select(
                CytoscapeConnection.node1,
                CytoscapeConnection.node2,
                CytoscapeConnection.connections,
            )
            .select_from(CytoscapeConnection)
            .where(CytoscapeConnection.metagenome_id == metagenome_id)
        )
        if headers:
            start_nodes = {f"{header}s" for header in headers}
            end_nodes = {f"{header}e" for header in headers}
            nodes = start_nodes.union(end_nodes)
            stmt = stmt.where(
                or_(
                    CytoscapeConnection.node1.in_(nodes),
                    CytoscapeConnection.node2.in_(nodes),
                )
            )
        with Session(engine) as session:
            records = session.exec(stmt).all()
        stylesheet = [
            dict(
                selector=f"[label = {node1}]",
                style={"line-color": "blue", "opacity": 0.8},
            )
            for node1, *_ in records
        ]
        stylesheet += [
            dict(
                selector=f"[label = {node2}]",
                style={"line-color": "blue", "opacity": 0.8},
            )
            for _, node2, _ in records
        ]
        return stylesheet

    def has_user_refinements(self, metagenome_id: int) -> bool:
        with Session(engine) as session:
            refinement = session.exec(
                select(Refinement).where(
                    Refinement.metagenome_id == metagenome_id,
                    Refinement.initial_refinement == False,
                    Refinement.outdated == False,
                )
            ).first()
        if refinement:
            return True
        return False

    def get_refinements_row_data(
        self, metagenome_id: int
    ) -> List[
        Dict[
            Literal["refinement_id", "timestamp", "contigs"],
            Union[str, int, datetime],
        ]
    ]:
        stmt = select(Refinement).where(
            Refinement.metagenome_id == metagenome_id,
            Refinement.outdated == False,
            Refinement.initial_refinement == False,
        )
        data = []
        with Session(engine) as session:
            refinements = session.exec(stmt).all()
            for refinement in refinements:
                row = dict(
                    refinement_id=refinement.id,
                    timestamp=refinement.timestamp.strftime("%d-%b-%Y, %H:%M:%S"),
                    contigs=len(refinement.contigs),
                )
                data.append(row)
        return data

    def save_selections_to_refinement(
        self, metagenome_id: int, headers: List[str]
    ) -> None:
        with Session(engine) as session:
            contigs = session.exec(
                select(Contig).where(
                    Contig.metagenome_id == metagenome_id, Contig.header.in_(headers)
                )
            ).all()
            for contig in contigs:
                for refinement in contig.refinements:
                    refinement.outdated = True
            refinement = Refinement(
                contigs=contigs,
                metagenome_id=metagenome_id,
                outdated=False,
                initial_refinement=False,
            )
            session.add(refinement)
            session.commit()

    def get_refinements_dataframe(self, metagenome_id: int) -> pd.DataFrame:
        stmt = select(Refinement).where(
            Refinement.metagenome_id == metagenome_id,
            Refinement.outdated == False,
        )
        data = []
        with Session(engine) as session:
            refinements = session.exec(stmt).all()
            for refinement in refinements:
                data.append(
                    dict(
                        refinement_id=f"refinement_{refinement.id}",
                        timestamp=refinement.timestamp.strftime("%d-%b-%Y"),
                        contig=[contig.header for contig in refinement.contigs],
                    )
                )
        return pd.DataFrame(data).explode("contig")
