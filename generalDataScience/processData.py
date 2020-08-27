import sys,datetime
import pandas as pd
import numpy as np
import re

auxFile = open(sys.argv[1], 'r')
fileStrs = []

for i in range(1, 22):
    currentStr = auxFile.readline()
    fileStrs.append(currentStr)
    print(currentStr)
    auxStartMatch = re.search('Waveform Type', currentStr)
    vertScaleMatch = re.search('Vertical Scale', currentStr)
    auxEndMatch = re.search('Vertical Position', currentStr)
    endingMatch = re.search('Label', currentStr)
    if vertScaleMatch:
        vertScale = currentStr.split(',')[1:]
        vertScale[-1] = vertScale[-1].replace('\n','')
        for count,i in enumerate(vertScale):
            vertScale[count] = float(i)
    if auxStartMatch:
        auxStart = i
    if auxEndMatch:
        auxEnd = i
    if endingMatch:
        testLabels = currentStr.replace('Label,','')
        divider = i
        headers = auxFile.readline()
        auxFile.close()
        break

auxdf = pd.read_csv(sys.argv[1], header=None,skiprows=auxStart-1, nrows=auxEnd-auxStart+1)

channels = headers.replace('TIME,','')
headers = headers.split(',')
headers[-1] = headers[-1].replace('\n','')

start = int(sys.argv[2])
end = int(sys.argv[3])
if start == 0:
    start = 1
if end == 0:
    end = 10_000_000
df = pd.read_csv(sys.argv[1], names = headers, skiprows=divider+start, nrows=end, engine='c', memory_map=True).astype('float64')

waveFormTypes = sys.argv[4:-1]
for n,i in enumerate(waveFormTypes):
    waveFormTypes[n] = i.replace(',','')
name = sys.argv[-1]

for i in headers:
    df[i].to_hdf(f'{name}_{i}.h5', key='df', mode='w')

auxdf.to_csv(f'{sys.argv[-1]}auxdf.csv')

vertScale = str(vertScale).replace('[','')
vertScale = vertScale.replace(']','')

waveFormTypes = str(waveFormTypes).replace('[','')
waveFormTypes = waveFormTypes.replace(']','')
waveFormTypes = waveFormTypes.replace("'",'')

f = open(f'{name}Attributes.csv', 'w')
f.write(channels)
f.write(vertScale+'\n')
f.write(waveFormTypes+'\n')
f.write(testLabels)
f.write(f'{datetime.datetime.now().strftime("%X")} ')
f.write(f'{datetime.datetime.now().strftime("%x")}')
f.close()
