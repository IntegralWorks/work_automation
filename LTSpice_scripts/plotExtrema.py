import sys
import pandas as pd
import numpy as np
from scipy.signal import find_peaks,argrelextrema
from matplotlib import pyplot as plt

f = open(sys.argv[1],'r')

data = []
for i in f.readlines():
    data.append(i.replace('\t',','))
f.close()

f2 = open(f"{sys.argv[1].replace('.txt','')}.csv",'w+')

for i in data:
    f2.write(i)

df = pd.read_csv(f"{sys.argv[1].replace('.txt','')}.csv",engine='c')

time = pd.Series(df['time']).to_numpy()
Vin = pd.Series(df['V(vin)']).to_numpy()
VinMaxima = find_peaks(Vin)
VinMinima = find_peaks(-Vin)
Vout = pd.Series(df['V(vout)']).to_numpy()
VoutMaxima = find_peaks(Vout)
VoutMinima = find_peaks(-Vout)

minimaTimeDeltas = {}
minimaVoltageDeltas = {}
maximaTimeDeltas = {}
maximaVoltageDeltas = {}
n = 0
for A,B,C,D in zip(VinMaxima[0], VoutMaxima[0], VinMinima[0], VoutMinima[0]):
    maximaTimeDeltas[n] = time[A]-time[B]
    maximaVoltageDeltas[n] = Vin[A]-Vout[B]
    minimaTimeDeltas[n] = time[C]-time[D]
    minimaVoltageDeltas[n] = Vin[C]-Vout[D]
    n+=1
plt.figure(0)
plt.plot(df['time'],df['V(vin)'])
plt.plot(df['time'],df['V(vout)'])

plt.figure(1)
plt.title('maximaTimeDeltas')
plt.plot(*zip(*maximaTimeDeltas.items()))
plt.figure(2)
plt.title('maximaVoltageDeltas')
plt.plot(*zip(*maximaVoltageDeltas.items()))
plt.figure(3)
plt.title('minimaTimeDeltas')
plt.plot(*zip(*minimaTimeDeltas.items()))
plt.figure(4)
plt.title('minimaVoltageDeltas')
plt.plot(*zip(*minimaVoltageDeltas.items()))
plt.show()
