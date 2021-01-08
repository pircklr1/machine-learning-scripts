#!/usr/bin/env python
"""
Performance monitoring
"""

import os, sys, pickle
import numpy as np
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.covariance import EllipticEnvelope
from scipy.stats import wasserstein_distance

from cslib import fetch_ts
def get_latest_train_data(country):
    """
    load the data used in the latest training
    """

    data_dir = os.path.join("data","cs_train","data")
    ts_data = fetch_ts(data_dir)
        
    for c,df in ts_data.items():
        if(c==country):
            return df


if __name__ == "__main__":

    ## get latest training data
    data = get_latest_train_data("spain")