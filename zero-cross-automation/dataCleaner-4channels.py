import csv
import pandas as pd
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft

df = pd.read_csv(sys.argv[1], engine='c')
tmpdf = df.loc[:, df.dtypes == np.float64]
tmpdf = tmpdf.drop("F",axis = 1)
tmpdf = tmpdf.drop("K",axis = 1)
tmpdf = tmpdf.drop("R",axis = 1)
tmpdf.to_csv('cleanData.csv')
