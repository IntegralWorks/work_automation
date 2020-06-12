import csv
import pandas as pd
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft

df = pd.read_csv(sys.argv[1], engine='c')

time = pd.Series(df.loc[:, "D"]).to_numpy()
CH1 = pd.Series(df.loc[:, "E"]).to_numpy()
CH2 = pd.Series(df.loc[:, "K"]).to_numpy()
CH3 = pd.Series(df.loc[:, "Q"]).to_numpy()
CH4 = pd.Series(df.loc[:, "W"]).to_numpy()

#where in the time array did a possible zero-cross occur
zeroCrossTimeIndicesCH1 = np.array([])
zeroCrossTimeIndicesCH2 = np.array([])

#the candidate pairs recorded
zeroCrossPairsCH1 = np.array([])
zeroCrossPairsCH1.shape=(0,2)
zeroCrossPairsCH2 = np.array([])
zeroCrossPairsCH2.shape=(0,2)

zcDictionaryCH1 = {}
zcDictionaryCH2 = {}

for i in range(1, len(time)):
    compareCH1 = CH1[i]*CH1[i-1]
    compareCH2 = CH2[i]*CH2[i-1]

    if compareCH1 <= 0:
        zeroCrossTimeIndicesCH1 = np.append(zeroCrossTimeIndicesCH1, i) #here we just appended the index of the time array matching the condition
        
        zeroCrossPairsCH1 = np.concatenate((zeroCrossPairsCH1, [[CH1[i-1],CH1[i]]])) #then we record the candidate pair
        zcDictionaryCH1[i] = [CH1[i-1],CH1[i]] #the coup de grace is then making an associative array binding each time index to the candidate pair
            
    if compareCH2 <= 0:
        zeroCrossTimeIndicesCH2 = np.append(zeroCrossTimeIndicesCH2, i)
        
        zeroCrossPairsCH2 = np.concatenate((zeroCrossPairsCH2, [[CH2[i-1],CH2[i]]])) #https://stackoverflow.com/questions/26969563/how-can-i-vertically-concatenate-1x2-arrays-in-numpy
        zcDictionaryCH2[i] = [CH2[i-1],CH2[i]]

zeroCrossTimeIndicesCH1 = zeroCrossTimeIndicesCH1.astype(np.int)
zeroCrossTimeIndicesCH2 = zeroCrossTimeIndicesCH2.astype(np.int)

timeCH1 = np.array([])
#timeCH1.shape=(0,1)
timeCH2 = np.array([])
#timeCH2.shape=(0,1)
def getTimeValues(timeCH, zeroCrossTimeIndices):
    for i in zeroCrossTimeIndices:
        timeCH = np.concatenate((timeCH, [time[i]]))
    return timeCH

timeCH1 = getTimeValues(timeCH1,zeroCrossTimeIndicesCH1)
timeCH2 = getTimeValues(timeCH2,zeroCrossTimeIndicesCH2)


def acquireZeroCrosses():
    plt.plot(time, CH1)
    plt.scatter(timeCH1,zeroCrossPairsCH1[:,0])
    plt.scatter(timeCH1,zeroCrossPairsCH1[:,1])
    plt.plot(time, CH2)
    plt.scatter(timeCH2,zeroCrossPairsCH2[:,0])
    plt.scatter(timeCH2,zeroCrossPairsCH2[:,1])
    plt.show()

acquireZeroCrosses()
