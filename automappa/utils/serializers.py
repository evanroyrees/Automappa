#!/usr/bin/env python

import os
import logging
import base64
from datetime import datetime
import io
import pandas as pd

from dash import html

import psycopg2
from sqlalchemy import create_engine

from autometa.common.markers import load as load_markers
from autometa.common.metagenome import Metagenome

logging.basicConfig(
    format="[%(levelname)s] %(name)s: %(message)s",
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)



POSTGRES_URL = os.environ.get("POSTGRES_URL")

def parse_contig_annotations(contents: str, filename: str) -> pd.DataFrame:
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    df = pd.DataFrame()
    if "csv" in filename:
        # Assume that the user uploaded a CSV file
        df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    elif "xls" in filename:
        # Assume that the user uploaded an excel file
        df = pd.read_excel(io.BytesIO(decoded))
    elif ".tsv" in filename:
        # Assume that the user uploaded an excel file
        df = pd.read_csv(
            io.StringIO(decoded.decode("utf-8")),
            sep="\t",
        )
    if "contig" not in df.columns:
        raise ValueError(f"contig not in {df.columns}")
    if df.empty:
        raise ValueError(f"{filename} is empty!")
    return df


def store_binning_main(filepath: str, session_uid: str) -> html.Div:
    try:
        df = pd.read_csv(filepath, sep="\t")
        engine = create_engine(url=POSTGRES_URL, echo=False)
        table_name = f"{session_uid}-binning"
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        logger.debug(f"{filepath} ({df.shape[0]:,} contigs) saved to datatable {table_name}")
    except Exception as err:
        logger.error(err)
        return html.Div(["There was an error processing this file."])
    filename = os.path.basename(filepath)
    timestamp = os.path.getmtime(filepath)
    last_modified = datetime.fromtimestamp(timestamp).strftime("%Y-%b-%d, %H:%M:%S")
    return html.Div(
        [
            html.H5("binning-main annotations uploaded:"),
            html.H6(f"filename: {filename}"),
            html.H6(f"last modified: {last_modified}"),
            html.H6(f"contigs: {df.shape[0]:,}, columns: {df.shape[1]}"),
            html.Pre(f"table_name: {table_name}"),
        ]
    )

def read_binning_main(session_uid: str)->pd.DataFrame:
    table_name = f"{session_uid}-binning"
    return retrieve_datatable(table_name)

def retrieve_datatable(table_name: str) -> pd.DataFrame:
    engine = create_engine(url=POSTGRES_URL, echo=False)
    if not engine.has_table(table_name):
        tables = engine.table_names()
        raise ValueError(f"{table_name} not in postgres database! available: {tables}")
    engine.table_names()
    df = pd.read_sql(table_name, engine).set_index("contig")
    logger.debug(f"retrieved {df.shape[0]} contigs from {table_name} datatable")
    return df

def store_markers(filepath: str, session_uid: str) -> html.Div:
    try:
        df = load_markers(filepath)
        engine = create_engine(url=POSTGRES_URL, echo=False)
        table_name = f"{session_uid}-markers"
        df.to_sql(table_name, engine, if_exists='replace', index=True)
        logger.debug(f"{filepath} ({df.shape[0]:,} contigs) saved to datatable {table_name}")
    except Exception as err:
        logger.error(err)
        return html.Div(["There was an error processing this file."])
    timestamp = os.path.getmtime(filepath)
    last_modified = datetime.fromtimestamp(timestamp).strftime("%Y-%b-%d, %H:%M:%S")
    filename = os.path.basename(filepath)
    return html.Div(
        [
            html.H5("markers annotations uploaded:"),
            html.H6(f"filename: {filename}"),
            html.H6(f"last modified: {last_modified}"),
            html.H6(f"contigs: {df.shape[0]:,}, markers: {df.shape[1]}"),
            html.Pre(f"table_name: {table_name}"),
        ]
    )


def store_metagenome(filepath: str, session_uid: str) -> html.Div:
    try:
        metagenome = Metagenome(assembly=filepath)
        logger.debug(f"{filepath} uploaded... saving to datatable...")
        df = pd.DataFrame(
            [{"contig":seqrecord.id, "sequence":str(seqrecord.seq)} for seqrecord in metagenome.seqrecords]
        )
        engine = create_engine(url=POSTGRES_URL, echo=False)
        table_name = f"{session_uid}-metagenome-seqrecords"
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        logger.debug(f"{filepath} ({df.shape[0]:,} contigs) saved to datatable {table_name}")
    except Exception as err:
        logger.error(err)
        return html.Div(["There was an error processing this file."])
    filename = os.path.basename(filepath)
    timestamp = os.path.getmtime(filepath)
    last_modified = datetime.fromtimestamp(timestamp).strftime("%Y-%b-%d, %H:%M:%S")
    # TODO: Store parsed data
    tables = engine.table_names()
    return html.Div(
        [
            html.H5("metagenome assembly uploaded:"),
            html.H6(f"filename: {filename}"),
            html.H6(f"last modified: {last_modified}"),
            html.H6(f"nseqs: {metagenome.nseqs:,}, size: {metagenome.size:,} (bp)"),
            html.Pre(f"all tables in pgdb: {', '.join(tables)}"),
        ]
    )


if __name__ == "__main__":
    pass
