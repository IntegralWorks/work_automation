import sys
import datetime as dt
import time
import pyvisa as visa
import matplotlib
matplotlib.use('Cairo') #resolves backend performance issues
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from io import StringIO, BytesIO
import xlsxwriter as excel
import re

"""
system argument/anatomy of a script call:

py captureScopeData.py -notrig/-forcetrig $NAME $XC-POINT $CH1...

py: python interpreter (call with 'py' or 'python' in cmd)

captureScopeData.py: name of script

-notrig/-forcetrig: the function/subroutine setupTrigger() is configured to activate if sys.argv[1]=='-forcetrig'. '-notrig' is just syntactical sugar
for literally any other string under the sun.

$NAME: user-defined name of the test, i.e. ParallelHalfLoad or BatteryDrainTest etc.

$XC-POINT: a floating-point value that represents what "x-cross" the user wants to see. That is, say you have a sample on the scope, 
and you want to see the following data from channels "CH1" and "CH2":

    I. When the waveform(s) hits zero
    II. When the waveform(s) hits 7.5
    III. When the waveform(s) hits [some value n]

Then you'd call the script thrice like this:

py captureScopeData.py -notrig ZeroTest 0 CH1 CH2
py captureScopeData.py -notrig 7.5Test 7.5 CH1 CH2
py captureScopeData.py -notrig nTest $n CH1 CH2 //(where n is some arbitrary number)

You'd get three spreadsheets. Also, only the $XC-POINT value has to change. you can also do

py captureScopeData.py -notrig test 0 CH1 CH2
py captureScopeData.py -notrig test 7.5 CH1 CH2
py captureScopeData.py -notrig test $n CH1 CH2 //(where n is some arbitrary number)

you will get three spreadsheets with the name "test" in them but the filename will still be different (reflects the different x-cross value)

$CH1...: the channels chosen to graph *and* compare. This is the most sensitive argument as if the channel and x-cross value max out the scope [the scope can only search
so many values per channel] it can break the code for various reasons. This will be handled in the future by including a config system that abstracts system arguments.
"""

rm = visa.ResourceManager()
for n,i in enumerate(rm.list_resources()):
    if re.search('TCPIP',i):
        print(f'instrument:{i} index: {n}')     

scope = rm.open_resource(rm.list_resources()[int(input('select a scope\n'))])

def openChannels():
    scope.write(f'select:CH1 1')
    scope.write(f'select:CH2 1')
    scope.write(f'select:CH3 1')
    scope.write(f'select:CH4 1')

def closeAllChannelsExceptOne(CH):
    CH_list = ['CH1','CH2','CH3','CH4']
    CH_list.pop(CH_list.index(f'{CH}'))
    scope.write(f'select:{CH_list[0]} 0')
    scope.write(f'select:{CH_list[1]} 0')
    scope.write(f'select:{CH_list[2]} 0')

openChannels()

scope.timeout = 10000 # ms
scope.encoding = 'latin_1'
scope.read_termination = '\n'
scope.write_termination = None
scope.write('*cls') # clear ESR
scope.write('header OFF') # disable attribute echo in replies

print(scope.query('*idn?'))

# prompt
input("""
ACTION:
Press Enter to begin.
""")
scope.write(f':SEARCH:SEARCH1:STATE 0')
# default setup
#scope.write('*rst')
t1 = time.perf_counter()
r = scope.query('*opc?') # sync
t2 = time.perf_counter()
print('reset time: {}'.format(t2 - t1))

# autoset
#scope.write('autoset EXECUTE')
t3 = time.perf_counter()
r = scope.query('*opc?')
t4 = time.perf_counter()
print('autoset time: {} s'.format(t4 - t3))

# acquisition
def setupTrigger():
    scope.write('acquire:state OFF') # stop
    scope.write('acquire:stopafter SEQUENCE;state ON') # single
    t5 = time.perf_counter()
    r = scope.query('*opc?')
    t6 = time.perf_counter()
    print('acquire time: {} s'.format(t6 - t5))
if '-forcetrig' in sys.argv[1:]:
    setupTrigger()

def dataQuery(num):
    # curve configuration
    scope.write('data:encdg SRIBINARY') # signed integer
    scope.write(f'data:source CH{num}')
    scope.write(f'data:start 1')
    acq_record = int(scope.query('horizontal:recordlength?'))
    scope.write('data:stop {}'.format(acq_record))
    scope.write('wfmoutpre:byt_n 1') # 1 byte per sample

    # data query
    t7 = time.perf_counter()
    bin_wave = scope.query_binary_values('curve?', datatype='b', container=np.array)
    t8 = time.perf_counter()
    print(f'CH{num} transfer time: {t8 - t7} s')
    return bin_wave
CH1_binWave = dataQuery(1)
CH2_binWave = dataQuery(2)
CH3_binWave = dataQuery(3)
CH4_binWave = dataQuery(4)

# retrieve scaling factors
wfm_record = int(scope.query('wfmoutpre:nr_pt?'))
pre_trig_record = int(scope.query('wfmoutpre:pt_off?'))
t_scale = float(scope.query('wfmoutpre:xincr?'))
t_sub = float(scope.query('wfmoutpre:xzero?')) # sub-sample trigger correction
v_scale = float(scope.query('wfmoutpre:ymult?')) # volts / level
v_off = float(scope.query('wfmoutpre:yzero?')) # reference voltage
v_pos = float(scope.query('wfmoutpre:yoff?')) # reference position (level)

# error checking
r = int(scope.query('*esr?'))
print('event status register: 0b{:08b}'.format(r))
r = scope.query('allev?').strip()
print('all event messages: {}'.format(r))

# disconnect
def closeObjects():
    scope.close()
    rm.close()

def XCross(X, CH_list):
    xcData = {}
    for CH in CH_list:
        scope.write(f':SEARCH:SEARCH1:TRIGger:A:EDGE:SOUrce {CH}')
        scope.write(f':SEARCH:SEARCH1:TRIGger:A:LOWerthreshold:{CH} {float(X)}')
        scope.write(f':SEARCH:SEARCH1:TRIGger:A:EDGE:SLOpe EITHER')
        scope.write(f':SEARCH:SEARCH1:STATE 1')
        time.sleep(6)
        scope.write('mark:saveall touser')
        tmpstr = StringIO(scope.query('mark:userlist?').replace(';','\n'))
        time.sleep(2)
        scope.write(f'mark:delete {CH}')
        scope.write(f':SEARCH:SEARCH1:STATE 0')
        time.sleep(2)
        df = pd.read_csv(tmpstr, index_col=0, header=None)
        xcData[CH] = df[4].rename(f'{CH}')
    return xcData

xcData = XCross(sys.argv[3], sys.argv[4:])
#py -i captureScopeData.py -notrig sqWaveTest 1 CH1

# create scaled vectors
# horizontal (time)
total_time = t_scale * wfm_record
t_start = (-pre_trig_record * t_scale) + t_sub
t_stop = t_start + total_time
scaled_time = np.linspace(t_start, t_stop, num=wfm_record, endpoint=False)

# vertical (voltage)
def transcribeWaves(wave):
    unscaled_wave = np.array(wave, dtype='double') # data type conversion
    scaled_wave = (unscaled_wave - v_pos) * v_scale + v_off
    return scaled_wave
CH1 = transcribeWaves(CH1_binWave)
CH2 = transcribeWaves(CH2_binWave)
CH3 = transcribeWaves(CH3_binWave)
CH4 = transcribeWaves(CH4_binWave)

channelDict = {
'CH1':CH1,
'CH2':CH2,
'CH3':CH3,
'CH4':CH4
}

"""
Documentation for the splitData(...) function
Remember that 10 items in a list are [0,1,2,3,4,5,6,7,8,9]. This is the first index of the splitDataDict. each index represents about 1 million points of
oscilloscope data.
Second, the second index runs from [0,1,2,3,4]. This is a deliberate choice, and the items are listed here:
    0: the scaled_time values, or raw time values at this "slice." [a slice in this context means say 0 to 1_000_000. we want to go +=1_000_000 until we're done.]
    1: the voltage values, or raw voltage values at this "slice."
    2: this is the tricky part. this section is the "x-crosses within this slice", but more specifically it means the indices of the zero-cross data itself.
        so if the item says say array([43, 44, 45, 46, 47], dtype=int64) then that means xcData['whatever'][43] equals a time value from the scope itself
        that matched the Search function of the scope.
    3: the color of the channel plot.
    4. the color of the scatter [x-cross] plot.
"""
def splitData(time, xcDict, chDict, keys):
    maxSize = len(time)
    pieceSize = len(time)/10
    splitDataDict = {CH: [] for CH in keys}

    for k in splitDataDict.keys():
        if k == 'CH1':
            plotColor = 'yellow'
            scatterColor = 'red'
        if k == 'CH2':
            plotColor = 'cyan'
            scatterColor = 'orange'
        if k == 'CH3':
            plotColor = 'purple'
            scatterColor = 'pink'
        if k == 'CH4':
            plotColor = 'green'
            scatterColor = 'black'

        for i in range(1,11):
            a = int((i-1)*pieceSize)
            b = int(i*pieceSize)-1
            mathHack = np.where((xcDict[k] > scaled_time[a]) & (xcDict[k] < scaled_time[b]))
            mathHack = mathHack[0]
            entry = [time[a:b] , chDict[k][a:b] , mathHack, plotColor, scatterColor]
            splitDataDict[k].append(entry) #time, voltage, xc -- all sliced up

    return splitDataDict

splitDataDict = splitData(scaled_time, xcData, channelDict, sys.argv[4:])

def xcDelta(CH_A, CH_B):
    A = CH_A.to_numpy()
    B = CH_B.to_numpy()
    C = A-B
    A = pd.Series(A)
    B = pd.Series(B)
    C = pd.Series(C)
    result = pd.DataFrame({CH_A.name : A, CH_B.name : B, f'{CH_A.name} minus {CH_B.name} delta' : C}).reset_index()
    return result

splitDataDict = splitData(scaled_time, xcData, channelDict, sys.argv[4:])

def graphSplitData(d,xcData):
    keys = list(d.keys())
    counter = 1
    images = []
    flag = False
    cursorPolarity = True
    while flag != True:
        for k in keys:
            plt.title(f'Points {0+(counter-1)*1_000_000} to {1_000_000*counter}')
            plt.xlabel('time (seconds)')
            plt.ylabel('voltage (volts)')
            plt.plot(d[k][counter-1][0],d[k][counter-1][1],color=d[k][counter-1][3],zorder=1)
            plt.scatter(xcData[k][d[k][counter-1][2]],np.ones(len(d[k][counter-1][2]))*float(sys.argv[3]),color=d[k][counter-1][4], marker='o', s = 1, zorder=2)
            cursors = xcData[k][d[k][counter-1][2]]
            plt.vlines(cursors, ymin=float(sys.argv[3]), ymax=plt.gca().get_ylim()[cursorPolarity],color=d[k][counter-1][3])
            cursorPolarity = not cursorPolarity
            for xc in cursors:
                #plt.axvline(x=xc, label=f'cursor position: {xc} s',color='black', linewidth = .1, zorder=0)
                plt.text(xc, plt.gca().get_ylim()[cursorPolarity]/2 ,f'{xc}', verticalalignment='center')
        pic = BytesIO()
        figure = plt.gcf()
        figure.set_size_inches(100,7)
        print(f'Saving image {counter} ...')
        ts = time.perf_counter()
        plt.savefig(pic, pad_inches = 0, bbox_inches = 'tight', format='png')
        images.append(pic)
        tend = time.perf_counter()
        print(f' Saving image {counter} time: {tend - ts} s')
        plt.close()
        if counter == 10:
            flag = True
            return images
        counter +=1

graphs = graphSplitData(splitDataDict,xcData)

def exportGraphs(graphs, deltaData, x_point):
    filename = 'dummy.png'
    workbook = excel.Workbook(f'{sys.argv[2]}DataReportAt{x_point}Cross.xlsx')
    worksheet = workbook.add_worksheet(f'{x_point}-Cross images')
    deltaSheet = workbook.add_worksheet('Deltas')
    counter = 1
    for i in graphs:
        worksheet.insert_image(f'A{counter}', filename, {'image_data' : i})
        counter+=31
    y1 = 0
    x2 = 0
    for k in deltaData.keys()[1:]:
        deltaSheet.write_row(0, y1, [deltaData[k].name])
        deltaSheet.write_column(1, x2, deltaData[k].to_list())
        y1+=1
        x2+=1
    workbook.close()

deltas = xcDelta(xcData['CH1'],xcData['CH4'])

exportGraphs(graphs, deltas, sys.argv[3])

def saveData():
    timestamp = f'{dt.datetime.now().strftime("%x")}_{dt.datetime.now().strftime("%X")}'
    np.save(f'TIME_{sys.argv[2]}_{timestamp.replace(":","-").replace("/","-")}',scaled_time)
    np.save(f'CH1_{sys.argv[2]}_{timestamp.replace(":","-").replace("/","-")}',CH1)
    np.save(f'CH2_{sys.argv[2]}_{timestamp.replace(":","-").replace("/","-")}',CH2)
    np.save(f'CH3_{sys.argv[2]}_{timestamp.replace(":","-").replace("/","-")}',CH3)
    np.save(f'CH4_{sys.argv[2]}_{timestamp.replace(":","-").replace("/","-")}',CH4)
