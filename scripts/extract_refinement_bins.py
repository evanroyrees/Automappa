#!/usr/bin/env python
# -*- coding: utf-8 -*-

from io import TextIOWrapper
from sys import exit
from typing import List, Tuple
import argparse
import os
import pandas as pd


def fasta_parser(handle: TextIOWrapper):
    for line in handle:
        if line[0] == ">":
            title = line[1:].rstrip()
            contig_id = title.split(None, 1)[0]
            break
    else:
        # no break encountered - probably an empty file
        return
    lines = []
    for line in handle:
        if line[0] == ">":
            yield title, "".join(lines).replace(" ", "").replace("\r", "")
            lines = []
            title = line[1:].rstrip()
            contig_id = title.split(None, 1)[0]
            continue
        lines.append(line.rstrip())

    yield contig_id, "".join(lines).replace(" ", "").replace("\r", "")


def fasta_writer(records: List[Tuple[str, str]], out: str) -> None:
    lines = ""
    n_records = 0
    for record, seq in records:
        lines += f">{record}\n{seq}\n"
        n_records += 1
    with open(out, "w") as fh:
        fh.write(lines)
    return n_records


def get_contigs(df: pd.DataFrame, column: str) -> List:
    columns = df.columns.tolist()
    if column not in columns:
        print(f"{column} not in `df` columns")
        print(f"Available columns are: {', '.join(columns)}")
        return []
    else:
        return set(df[column].index.tolist())


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
    with open(args.fasta) as fh:
        records = {record: seq for record, seq in fasta_parser(fh) if record in contigs}
    print(f"# {len(records):,} records in {args.fasta}")
    outdir = args.output if args.output else column
    print(f"# Writing refinement groupings to {outdir}")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    print(f"bin\tnum. sequences")
    for refined_bin, dff in df.groupby(column):
        bin_contigs = set(dff.index.tolist())
        bin_records = [
            (record, seq) for record, seq in records.items() if record in bin_contigs
        ]
        out = os.path.join(outdir, f"{refined_bin}.fasta")
        n_written = fasta_writer(records=bin_records, out=out)
        print(f"{refined_bin}\t{n_written}")


if __name__ == "__main__":
    main()
