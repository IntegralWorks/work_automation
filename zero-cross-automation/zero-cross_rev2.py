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
zeroCrossHitsCH2 = np.array([])

#need the indices of the time array
hitIndicesCH1 = np.array([])
hitIndicesCH2 = np.array([]) 

#for the rare edge case in which the scope actually reports a real zero.
#record the time it happened and the pair of values [by noting the index]
actualZerosCH1 = np.array([])
actualZerosCH2 = np.array([])

counterCH1 = 0
counterCH2 = 0
for i in range(1, len(time)):
    compareCH1 = CH1[i]*CH1[i-1]
    compareCH2 = CH2[i]*CH2[i-1]
    if compareCH1 <= 0:
        zeroCrossHitsCH1 = np.append(zeroCrossHitsCH1,np.float64(time[i]))
        hitIndicesCH1 = np.append(hitIndicesCH1, i)
        counterCH1 += 1
        try:
            if zeroCrossHitsCH1[counter] == 0:
                actualZerosCH1 = np.append(actualZerosCH1, hitIndicesCH1[counter])
        except: 
            pass


    if compareCH2 <= 0:
        zeroCrossHitsCH2 = np.append(zeroCrossHitsCH2,np.float64(time[i]))
        hitIndicesCH2 = np.append(hitIndicesCH1, i)
        counterCH2 += 1
        try:
            if zeroCrossHitsCH1[counter] == 0:
                actualZerosCH2 = np.append(actualZerosCH2, hitIndicesCH2[counter])
        except: 
            pass


print(f'counterCH1 was {counterCH1}, counterCH2 was {counterCH2}, and we found {zeroCrossHitsCH1.shape}, {zeroCrossHitsCH2.shape}  hits')
hitIndices = np.array([])
def locateZeroCrossHits(hitIndices, zeroCrossHits):
    for counter, value in enumerate(zeroCrossHits):
        #hitIndices = np.append(hitIndices, np.where(time==value[0:]))
        hitIndices = np.append(hitIndices, np.where(time==value))
    return hitIndices

#call it like this:
#hitIndices = locateZeroCrossHits(hitIndices, zeroCrossHitsCH1)
