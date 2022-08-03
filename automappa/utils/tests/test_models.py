import pytest

from automappa.utils.models import SampleTables, AnnotationTable

# @pytest.fixture()
# def sampletables_fixture():


def get_sampletable():
    return SampleTables(
        **{
            "metagenome": {"id": "2a32c68b68deb1b2c5c82871b592d392-metagenome"},
            "binning": {"id": "d92e6e59d3fb4f7d988ed6adf5e71cc4-binning"},
            "refinements": {"id": "d92e6e59d3fb4f7d988ed6adf5e71cc4-refinement"},
            "markers": {"id": "1bba604b9ebb737e20af35c66fa9cff9-markers"},
        }
    )


def get_no_binning_sampletable():
    return SampleTables(
        **{
            "metagenome": {"id": "2a32c68b68deb1b2c5c82871b592d392-metagenome"},
            "markers": {"id": "1bba604b9ebb737e20af35c66fa9cff9-markers"},
        }
    )
