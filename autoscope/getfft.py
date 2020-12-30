import sys
import datetime as dt
import time
import pyvisa as visa
import matplotlib
#matplotlib.use('Cairo') #resolves backend performance issues
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from io import StringIO, BytesIO
import xlsxwriter as excel
import re
from scipy.fft import fft, fftfreq, rfft, rfftfreq

rm = visa.ResourceManager()
for n,i in enumerate(rm.list_resources()):
    if re.search('TCPIP',i):
        print(f'instrument:{i} index: {n}')     

scope = rm.open_resource(rm.list_resources()[int(input('select a scope\n'))])

scope.timeout = 10000 # ms
scope.encoding = 'latin_1'
scope.read_termination = '\n'
scope.write_termination = None
scope.write('*cls') # clear ESR
scope.write('header OFF') # disable attribute echo in replies

print(scope.query('*idn?'))

# prompt
input("""
Press Enter to continue...
""")

CH_list = ['CH1','CH2','CH3','CH4']

def closeAllChannelsExceptOne(CH_list, CH):
    CH_list = ['CH1','CH2','CH3','CH4']
    CH_list.pop(CH_list.index(f'{CH}'))
    scope.write(f'select:{CH_list[0]} 0')
    scope.write(f'select:{CH_list[1]} 0')
    scope.write(f'select:{CH_list[2]} 0')
    scope.write(f'select:{CH} 1')

def captureData(CH_list):
    d = {}
    for CH in CH_list:
        closeAllChannelsExceptOne(CH_list, CH)
        # curve configuration
        scope.write('data:encdg SRIBINARY') # signed integer
        scope.write(f'data:source {CH}')
        scope.write('data:start 1')
        acq_record = int(scope.query('horizontal:recordlength?'))
        scope.write('data:stop {}'.format(acq_record))
        scope.write('wfmoutpre:byt_n 1') # 1 byte per sample

        # data query
        bin_wave = scope.query_binary_values('curve?', datatype='b', container=np.array)

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

        # create scaled vectors
        # horizontal (time)
        total_time = t_scale * wfm_record
        t_start = (-pre_trig_record * t_scale) + t_sub
        t_stop = t_start + total_time
        scaled_time = np.linspace(t_start, t_stop, num=wfm_record, endpoint=False)
        # vertical (voltage)
        unscaled_wave = np.array(bin_wave, dtype='double') # data type conversion
        scaled_wave = (unscaled_wave - v_pos) * v_scale + v_off

        # plotting
        d[CH] = scaled_wave
        if CH == 'CH1':
            d['TIME'] = scaled_time
            
        # plt.plot(d['TIME'], d[CH])
        # plt.title(f'{CH}') # plot label
        # plt.xlabel('time (seconds)') # x label
        # plt.ylabel('voltage (volts)') # y label
        # print("look for plot window...")
        
    # plt.show()
    return d

d = captureData(CH_list)

def generateFFTData(d, CH_list):
    # crucial guide: https://realpython.com/python-scipy-fft/
    sample_rate = 25e6 #ex. when the scope is "at 40 ms" the sample rate is 25MS/s
    duration = .4 #ex. when the scope is "at 40 ms" that is 10 divisions of 40 ms meaning the actual length of time taken place is 400 ms
    N = int(10e6) #number of points: you can do either sample_rate * duration or just use the scope's value
    d_fft = {}
    df = pd.DataFrame()
    loc = 1
    for i in CH_list:
        d_fft[i] = (rfftfreq(N, 1 / sample_rate), rfft(d[i]), f'{i} - Duration: {duration}; Sample Rate: {sample_rate}S/s') #xf, yf
        if i == 'CH1':
            df.insert(loc=0, column='Sample_Frequency', value = d_fft[i][0])
        df.insert(loc=loc, column=i+'_FFTValue', value = d_fft[i][1])
        loc+=1
    return (d_fft, df)
            
data = generateFFTData(d, CH_list)
d_fft = data[0]
df = data[1]

def plotChannelFFTs(d_fft):
    for k in d_fft.keys():
        plt.title(d_fft[k][2])
        plt.plot(d_fft[k][0], np.abs(d_fft[k][1]))
        plt.show()

#plotChannelFFTs(d_fft)
df.to_csv('out.csv')

def openChannels():
    scope.write(f'select:CH1 1')
    scope.write(f'select:CH2 1')
    scope.write(f'select:CH3 1')
    scope.write(f'select:CH4 1')

openChannels()        
# scope.close()
# rm.close()
