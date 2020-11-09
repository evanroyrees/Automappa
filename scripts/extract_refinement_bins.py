#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import exit
from typing import List
import argparse
import os
import pandas as pd

from Bio import SeqIO


def get_contigs(df: pd.DataFrame, column: str) -> List:
    columns = df.columns.tolist()
    if column not in columns:
        print(f"{column} not in `df` columns")
        print(f"Available columns are: {', '.join(columns)}")
        return []
    else:
        return df[column].index.tolist()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        help="refinements.csv",
        required=True,
    )
    parser.add_argument(
        "--fasta",
        help="Path to metagenome.fasta to extract corresponding sequences from `input`",
        required=True,
    )
    parser.add_argument(
        "--output",
        help="Path to output directory to write refinement bins (Default is header_column, i.e. refinement_2)",
    )
    parser.add_argument(
        "--column",
        help="""
        Retrieve refinement grouping from provided `column`
        Default will use the most recent refinement group based on
        the highest number in the refinement_<number> header
        """,
    )
    args = parser.parse_args()

    df = pd.read_csv(args.input, index_col="contig")
    # This is sorted least to most
    refinement_cols = [col for col in df.columns if "refinement_" in col]
    if not refinement_cols and not args.column:
        print(f"Failed to find refinement columns in {args.input}")
        exit(1)
    latest_refinement = refinement_cols.pop()
    column = args.column if args.column else latest_refinement
    contigs = get_contigs(df, column=column)
    if not contigs:
        exit(1)
    records = [
        record for record in SeqIO.parse(args.fasta, "fasta") if record.id in contigs
    ]
    outdir = args.output if args.output else column
    for refined_bin, dff in df.groupby(column):
        bin_records = [record for record in records if record.id in dff.index.tolist()]
        out = os.path.join(outdir, f"{refined_bin}.fasta")
        SeqIO.write(bin_records, out, "fasta")
    
    print(f"wrote refinement groupings to {outdir}")

if __name__ == "__main__":
    main()
