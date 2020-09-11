# mdo simple plot
# python v3.8.3, pyvisa v1.10.1
# should work with MSO70k, DPO7k, MSO5k, MDO4k, MDO3k, and MSO2k series
# 5/6 Series MSO 

# incompatible with TDS2k and TBS1k series (see tbs simple plot)
import sys
import datetime as dt
import time # std module
import pyvisa as visa# http://github.com/hgrecco/pyvisa
import matplotlib.pyplot as plt # http://matplotlib.org/
import numpy as np # http://www.numpy.org/
import pandas as pd
from io import StringIO

visa_address = 'TCPIP0::169.254.8.227::INSTR'

rm = visa.ResourceManager()
scope = rm.open_resource(visa_address)
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

#get misc info

# channelInfo = []
# for i in range (1,5):
#     f'CH{i}:'+'label?'
#     f'CH{i}:'+'probe:ID?'
#     f'CH{i}:'+'probe?'
#     f'CH{i}:'+'scale?'
#     # chStrs = [f'CH{i}:'+'label',]

#     # label = scope.query(:label?')
#     # robe = scope.query(f'CH{')

# # disconnect

def closeObjects():
    scope.close()
    rm.close()

def XCross(*args):
    xcData = {}
    CH_list = ['CH1','CH2','CH3','CH4']
    for CH in args:
        CH_list.pop(CH_list.index(f'{CH}'))
        scope.write(f'select:{CH_list[0]} 0')
        scope.write(f'select:{CH_list[1]} 0')
        scope.write(f'select:{CH_list[2]} 0')
        scope.write(f'select:{CH} 1')
        CH_list.append(CH)

        scope.write(f':SEARCH:SEARCH1:TRIGger:A:EDGE:SOUrce {CH}')
        scope.write(f':SEARCH:SEARCH1:TRIGger:A:LOWerthreshold:{CH} 0')
        scope.write(f':SEARCH:SEARCH1:TRIGger:A:EDGE:SLOpe EITHER')
        scope.write(f':SEARCH:SEARCH1:STATE 1')
        time.sleep(5)
        scope.write('mark:saveall touser')
        tmpstr = StringIO(scope.query('mark:userlist?').replace(';','\n'))
        time.sleep(3)
        df = pd.read_csv(tmpstr, index_col=0, header=None)
        xcData[CH] = df[4]
    scope.write(f'select:{CH_list[0]} 1')
    scope.write(f'select:{CH_list[1]} 1')
    scope.write(f'select:{CH_list[2]} 1')
    return xcData

xcData = XCross('CH1','CH2','CH3','CH4')

# closeObjects()

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

def graph(time, *args):
    title = []
    for i in args:
        plt.plot(time, i)
    plt.xlabel('time (seconds)')
    plt.ylabel('voltage (volts)')
    plt.show()

def xcGraph(time, xcDict, chDict, mrksize, mrkshape, *args):
    title = []
    colorDict = {
    'CH1':['yellow','red'],
    'CH2':['cyan','teal'],
    'CH3':['purple','magenta'],
    'CH4':['green','black']
    }
    for i in args:
        plt.plot(time, chDict[f'CH{i}'],color=colorDict[f'CH{i}'][0],zorder=1)
        plt.scatter(xcDict[f'CH{i}'],np.zeros(len(xcDict[f'CH{i}'])), np.ones(len(xcDict[f'CH{i}']))*mrksize, color=colorDict[f'CH{i}'][1], marker=mrkshape, zorder=2)
    plt.show()

# xcGraph(scaled_time, xcData, channelDict, 200, '.', *[1,2,3,4])
# xcGraph(scaled_time, xcData, channelDict, 400, '1', *[1,2,3,4])

def saveData():
    timestamp = f'{dt.datetime.now().strftime("%x")}_{dt.datetime.now().strftime("%X")}'
    np.save(f'TIME_{sys.argv[2]}_{timestamp.replace(":","-").replace("/","-")}',scaled_time)
    np.save(f'CH1_{sys.argv[2]}_{timestamp.replace(":","-").replace("/","-")}',CH1)
    np.save(f'CH2_{sys.argv[2]}_{timestamp.replace(":","-").replace("/","-")}',CH2)
    np.save(f'CH3_{sys.argv[2]}_{timestamp.replace(":","-").replace("/","-")}',CH3)
    np.save(f'CH4_{sys.argv[2]}_{timestamp.replace(":","-").replace("/","-")}',CH4)

#saveData()

print("\nend of demonstration")
