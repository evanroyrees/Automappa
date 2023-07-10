class MetagenomeSchema:
    pass


class ContigSchema:
    CONTIG = "contig"
    HEADER = "header"
    CLUSTER = "cluster"
    COMPLETENESS = "completeness"
    PURITY = "purity"
    COVERAGE_STDDEV = "coverage_stddev"
    GC_CONTENT_STDDEV = "gc_content_stddev"
    COVERAGE = "coverage"
    GC_CONTENT = "gc_content"
    LENGTH = "length"
    SUPERKINGDOM = "superkingdom"
    DOMAIN = "domain"
    PHYLUM = "phylum"
    CLASS = "class"
    KLASS = "klass"
    ORDER = "order"
    FAMILY = "family"
    GENUS = "genus"
    SPECIES = "species"
    TAXID = "taxid"
    X_1 = "x_1"
    X_2 = "x_2"


class MarkerSchema:
    QNAME = "qname"
    ORF = "orf"
    SACC = "sacc"
    SNAME = "sname"
    FULL_SEQ_SCORE = "full_seq_score"
    CUTOFF = "cutoff"
    CONTIG = "contig"


class CytoscapeConnectionSchema:
    NODE1 = "node1"
    INTERACTION = "interaction"
    NODE2 = "node2"
    CONNECTIONS = "connections"
    MAPPINGTYPE = "mappingtype"
    NAME = "name"
    CONTIGLENGTH = "contiglength"
