import sys,os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

try:
    os.mkdir(f"{sys.argv[1]}_Reports")
    #os.mkdir(f"{'_'.join(sys.argv[1:])}_Images")
except FileExistsError:
    pass

f = open(f'{sys.argv[1]}Attributes.csv', 'r')
headers = ['TIME'] + f.readline().split(",")
headers[-1] = headers[-1].replace('\n','')
scalingFactors = f.readline().split(",")
scalingFactors[-1] = scalingFactors[-1].replace('\n','')
scalingFactors = np.float64(scalingFactors)
testLabels = f.readline()
dataLabels = f.readline().split(",")
dataLabels[-1] = dataLabels[-1].replace('\n','')
timestamp = f.readline()
f.close()

dataDictionary = {}
for i in headers:
    dataDictionary[i] = pd.read_hdf(f'{sys.argv[1]}_{i}.h5', 'df',start=int(sys.argv[2]),stop=int(sys.argv[3]))

time = dataDictionary["TIME"].to_numpy()
CH1 = dataDictionary['CH1'].to_numpy()/scalingFactors[0]
CH2 = dataDictionary['CH2'].to_numpy()/scalingFactors[1]
CH3 = dataDictionary['CH3'].to_numpy()/scalingFactors[2]
CH4 = dataDictionary['CH4'].to_numpy()/scalingFactors[3]

CH1_PEAKS = find_peaks(CH1)
CH1_LOWS = find_peaks(-CH1)
CH2_PEAKS = find_peaks(CH2)
CH2_LOWS = find_peaks(-CH2)

plt.scatter(time[CH1_PEAKS[0]], CH1[CH1_PEAKS[0]],color='red')
plt.scatter(time[CH1_LOWS[0]], CH1[CH1_LOWS[0]],color='orange')
plt.scatter(time[CH2_PEAKS[0]], CH2[CH2_PEAKS[0]],color='black')
plt.scatter(time[CH2_LOWS[0]], CH2[CH2_LOWS[0]],color='grey')
plt.plot(time,CH1,color='yellow')
plt.plot(time,CH2,color='cyan')
plt.plot(time,CH3,color='purple')
plt.plot(time,CH4,color='green')
plt.show()
