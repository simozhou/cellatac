#!/usr/bin/python3

import scanpy as sc
import anndata as ad
import numpy as np
import pandas as pd
import scipy.io as sci
import scipy as ss
import episcanpy.api as epi
from MulticoreTSNE import MulticoreTSNE as TSNE
import argparse

min_score_value = 0.515
nrof_features   = 120000
ncpus           = 1

my_parser = argparse.ArgumentParser()

my_parser.add_argument("-m", "--min-score-value", type=float)
my_parser.add_argument("-f", "--nrof-features", type=int)
my_parser.add_argument("-p", "--ncpus", type=int)

args = my_parser.parse_args()

if args.min_score_value is not None:
  min_score_value = args.min_score_value

if args.nrof_features is not None:
  nrof_features = args.nrof_features

if args.ncpus is not None:
  ncpus = args.ncpus


mat = sci.mmread("mmtx/filtered_window_bc_matrix.mmtx.gz")
trans_mat = mat.transpose()
df = pd.DataFrame(trans_mat.toarray())
region_names = pd.read_table("mmtx/regions.names", header = None)
cell_names = pd.read_table("mmtx/cell.names", header = None)
df.columns=region_names[0]
df.index=cell_names[0]
adata = sc.AnnData(df)
adata.X = ss.sparse.csr_matrix(adata.X)
adata.var.index.name = 'region_names'
adata.obs.index.name = 'cell_names'
tsne = TSNE(n_jobs=ncpus)
epi.pp.lazy(adata)
epi.pp.normalize_total(adata)
epi.pp.cal_var(adata, save='episcanpy_variability.pdf')
epi.pl.variability_features(adata,log=None, min_score=min_score_value, nb_features=nrof_features, save='episcanpy_varfeat.pdf')
epi.pl.variability_features(adata,log='log10', min_score=min_score_value, nb_features=nrof_features, save='episcanpy_log_varfeat.pdf')
adata = epi.pp.select_var_feature(adata, nb_features=nrof_features, show=False, copy=True)
epi.tl.louvain(adata)
# epi.tl.getNClusters(adata, n_cluster=N_clusters)
epi.tl.leiden(adata)
# epi.tl.getNClusters(adata, n_cluster=N_clusters, method='leiden')   # note constant.
# umap has to be saved as .png as .pdf produces empty pdf files
epi.pl.umap(adata, color=['louvain', 'leiden'], wspace=0.4, save='.png')
adata.write("adata.h5ad", compression='gzip')
pd.DataFrame(adata.obs['louvain']).to_csv('Louvain.tsv', sep="\t", header=False)
pd.DataFrame(adata.obs['leiden']).to_csv('Leiden.tsv', sep="\t", header=False)


