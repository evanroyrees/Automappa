#!/usr/bin/env python

import argparse
import glob
import os
from typing import List

from autometa.binning.utilities import read_annotations


def find_annotations(dirpath: str) -> List[str]:
    annotation_globnames = ["*.coverages.tsv", "*.gc_content.tsv", "*.taxonomy.tsv", "*_bacteria_cache/superkingdom/superkingdom.am_clr_pca50_umap2.tsv.gz"]
    annotations = []
    for globname in annotation_globnames:
        search_str = os.path.join(dirpath, globname)
        annotations.extend([os.path.realpath(fp) for fp in glob.glob(search_str)])
    return annotations

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--autometa-results", help='Path to metagenome autometa results directory', required=True)
    parser.add_argument("--out", help="Path to write merged annotations table", required=True)
    args = parser.parse_args()

    annotations = find_annotations(args.autometa_results)
    df = read_annotations(annotations)
    df.to_csv(args.out, sep='\t', index=True, header=True)

if __name__ == "__main__":
    main()