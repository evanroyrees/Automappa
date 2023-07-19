import dash_mantine_components as dmc

from automappa.components import ids
from typing import Optional, Protocol, Tuple, Union


class SampleCardDataSource(Protocol):
    def get_metagenome_name(self, metagenome_id: int) -> str:
        """Get Metagenome.name where Metagenome.id == metagenome_id"""
        ...

    def contig_count(self, metagenome_id: int) -> int:
        ...

    def marker_count(self, metagenome_id: int) -> int:
        ...

    def connections_count(self, metagenome_id: int) -> int:
        ...

    def get_approximate_marker_sets(self, metagenome_id: int) -> int:
        ...

    def get_mimag_counts(self, metagenome_id: int) -> Tuple[int, int, int]:
        """Retrieve counts of clusters following MIMAG standards.

        standards:

        - High-quality >90% complete > 95% pure
        - Medium-quality >=50% complete > 90% pure
        - Low-quality <50% complete < 90% pure

        """
        ...

    def get_refinements_count(
        self, metagenome_id: int, initial: Optional[bool], outdated: Optional[bool]
    ) -> int:
        """Get Refinement count where Refinement.metagenome_id == metagenome_id

        Providing `initial` will add where(Refinement.initial_refinement == True)
        otherwise will omit this filter and retrieve all.

        Providing `outdated` will add where(Refinement.outdated == outdated)
        otherwise will omit this filter and retrieve all.
        """
        ...

    def get_refined_contig_count(self, metagenome_id: int) -> int:
        ...


def get_badge(label: str, id: dict[str, Union[str, int]], color: str) -> dmc.Badge:
    return dmc.Badge(label, id=id, color=color, variant="dot", size="xs")


def render(source: SampleCardDataSource, metagenome_id: int) -> dmc.Card:
    metagenome_badge = get_badge(
        label=ids.SAMPLE_CARD_METAGENOME_BADGE_LABEL,
        id={
            ids.SAMPLE_CARD_INDEX: metagenome_id,
            "type": ids.SAMPLE_CARD_METAGENOME_BADGE_TYPE,
        },
        color="lime",
    )
    contig_count = source.contig_count(metagenome_id)
    binning_badge = get_badge(
        label=f"{ids.SAMPLE_CARD_BINNING_BADGE_LABEL}: {contig_count:,}",
        id={
            ids.SAMPLE_CARD_INDEX: metagenome_id,
            "type": ids.SAMPLE_CARD_BINNING_BADGE_TYPE,
        },
        color="lime",
    )
    marker_count = source.marker_count(metagenome_id)
    marker_badge = get_badge(
        label=f"{ids.SAMPLE_CARD_MARKERS_BADGE_LABEL}: {marker_count:,}",
        id={
            ids.SAMPLE_CARD_INDEX: metagenome_id,
            "type": ids.SAMPLE_CARD_MARKERS_BADGE_TYPE,
        },
        color="lime",
    )
    connections_count = source.connections_count(metagenome_id)
    connections_badge = get_badge(
        label=ids.SAMPLE_CARD_CONNECTIONS_BADGE_LABEL,
        id={
            ids.SAMPLE_CARD_INDEX: metagenome_id,
            "type": ids.SAMPLE_CARD_CONNECTIONS_BADGE_TYPE,
        },
        color="lime" if connections_count > 0 else "red",
    )
    badges = [
        metagenome_badge,
        binning_badge,
        marker_badge,
        connections_badge,
    ]
    chip = dmc.Chip(
        "Select",
        id={
            ids.SAMPLE_CARD_INDEX: metagenome_id,
            "type": ids.SAMPLE_CARD_CHIP_TYPE,
        },
        size="sm",
        variant="outline",
        radius="xl",
        checked=False,
    )
    high_quality, medium_quality, low_quality = source.get_mimag_counts(metagenome_id)
    hiqh_quality_badge = dmc.Tooltip(
        label=">95% complete & >90% pure",
        position="top-end",
        offset=3,
        children=dmc.Badge(high_quality, color="lime", variant="filled"),
    )
    medium_quality_badge = dmc.Tooltip(
        label=(">=50% complete & >90% pure"),
        position="top",
        offset=3,
        children=dmc.Badge(medium_quality, color="yellow", variant="filled"),
    )
    low_quality_badge = dmc.Tooltip(
        label="<50% complete & <90% pure",
        position="top-start",
        offset=3,
        children=dmc.Badge(low_quality, color="orange", variant="filled"),
    )
    mimag_section = dmc.Center(
        dmc.Group(
            [
                hiqh_quality_badge,
                dmc.Divider(orientation="vertical", style={"height": 20}),
                medium_quality_badge,
                dmc.Divider(orientation="vertical", style={"height": 20}),
                low_quality_badge,
            ],
        ),
    )
    approx_markers = dmc.Group(
        [
            dmc.Text(f"Approx. Markers Sets:", size="xs"),
            dmc.Badge(
                source.get_approximate_marker_sets(metagenome_id),
                size="xs",
                variant="outline",
            ),
        ],
        position="apart",
    )
    uploaded_clusters = dmc.Group(
        [
            dmc.Text(f"Uploaded Clusters:", size="xs"),
            dmc.Badge(
                source.get_refinements_count(metagenome_id, initial=True),
                size="xs",
                variant="outline",
            ),
        ],
        position="apart",
    )
    user_refinements = dmc.Group(
        [
            dmc.Text(f"User Refinements:", size="xs"),
            dmc.Badge(
                source.get_refinements_count(
                    metagenome_id, initial=False, outdated=False
                ),
                size="xs",
                variant="outline",
            ),
        ],
        position="apart",
    )
    current_refinements = dmc.Group(
        [
            dmc.Text(f"Current Refinements:", size="xs"),
            dmc.Badge(
                source.get_refinements_count(metagenome_id, outdated=False),
                size="xs",
                variant="outline",
            ),
        ],
        position="apart",
    )
    refined_contig_count = source.get_refined_contig_count(metagenome_id)
    percent_clustered = round(refined_contig_count / contig_count * 100, 2)
    percent_clustered_text = dmc.Group(
        [
            dmc.Text(f"Contigs Clustered (%):", size="xs"),
            dmc.Badge(percent_clustered, size="xs", variant="outline"),
        ],
        position="apart",
    )
    return dmc.Card(
        id={ids.SAMPLE_CARD_INDEX: metagenome_id, "type": ids.SAMPLE_CARD_TYPE},
        children=[
            dmc.CardSection(
                dmc.Group(
                    dmc.Text(
                        source.get_metagenome_name(metagenome_id)
                        .replace("_", " ")
                        .title(),
                        weight=500,
                    ),
                ),
                withBorder=True,
                inheritPadding=True,
                py="xs",
            ),
            dmc.Space(h=10),
            dmc.SimpleGrid(cols=2, children=badges),
            dmc.Space(h=10),
            dmc.Text("MIMAG cluster counts", size="sm"),
            dmc.Space(h=5),
            mimag_section,
            dmc.Space(h=10),
            dmc.Divider(variant="dotted"),
            dmc.Space(h=10),
            approx_markers,
            uploaded_clusters,
            user_refinements,
            current_refinements,
            percent_clustered_text,
            dmc.Space(h=10),
            dmc.CardSection(dmc.Divider(variant="dashed"), withBorder=False),
            dmc.Space(h=10),
            dmc.Group(chip),
        ],
        withBorder=False,
        shadow="sm",
        radius="md",
        styles=dict(color="lime"),
    )
