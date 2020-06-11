import csv
import pandas as pd
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft

df = pd.read_csv(sys.argv[1], engine='c')

time = pd.Series(df.loc[:, "timeCH1"]).to_numpy()
CH1 = pd.Series(df.loc[:, "CH1"]).to_numpy()
CH2 = pd.Series(df.loc[:, "CH2"]).to_numpy()

zeroCrossHitsCH1 = np.array([])
zeroCrossPairsCH1 = np.zeros((np.size(time),2))
zeroCrossHitsCH2 = np.array([])
zeroCrossPairsCH2 = np.zeros((np.size(time),2))

#for the rare edge case in which the scope actually reports a real zero.
#record the time it happened and the pair of values
actualZeroesCH1 = np.zeros((np.size(time),3)) 
actualZeroesCH2 = np.zeros((np.size(time),3)) 

for i in range(1, len(time)):
    compareCH1 = CH1[i]*CH1[i-1]
    compareCH2 = CH2[i]*CH2[i-1]
    if compareCH1 <= 0:
        zeroCrossHitsCH1 = np.append(zeroCrossHitsCH1,np.float64(time[i]))
        zeroCrossPairsCH1[i] = [np.float64(CH1[i-1]),np.float64(CH1[i])]
        if zeroCrossPairsCH1[i-1][0] == 0 or zeroCrossPairsCH1[i][1] == 0:
            actualZeroesCH1 = [np.float64(time[i]), np.float64(CH1[i-1]),np.float64(CH1[i])]

    if compareCH2 <= 0:
        zeroCrossHitsCH2 = np.append(zeroCrossHitsCH2,np.float64(time[i]))
        zeroCrossPairsCH2[i] = [np.float64(CH2[i-1]),np.float64(CH2[i])]
        if zeroCrossPairsCH2[i-1][0] == 0 or zeroCrossPairsCH2[i][1] == 0:
            actualZeroesCH2 = [np.float64(time[i]), np.float64(CH2[i-1]),np.float64(CH2[i])]
