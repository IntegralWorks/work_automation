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

visa_address = 'TCPIP0::169.254.7.101::inst0::INSTR'

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
Connect probe to oscilloscope Channel 1 and the probe compensation signal.

Press Enter to continue...
""")

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
    print(f'CH{num}transfer time: {t8 - t7} s')
    return bin_wave
CH1_binWave = dataQuery(1)
CH2_binWave = dataQuery(2)

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
scope.close()
rm.close()

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

def classicGraph():
    plt.plot(scaled_time, CH1)
    plt.plot(scaled_time, CH2)
    plt.title('channel 1 and channel 2') # plot label
    plt.xlabel('time (seconds)') # x label
    plt.ylabel('voltage (volts)') # y label
    print("look for plot window...")
    plt.show()

def graph(time, *args):
    title = []
    for i in args:
        plt.plot(time, i)
        title.append('Placeholder_text')
    plt.xlabel('time (seconds)')
    plt.ylabel('voltage (volts)')
    plt.show()



timestamp = f'{dt.datetime.now().strftime("%x")}_{dt.datetime.now().strftime("%X")}'
np.save(f'{sys.argv[2]}_{timestamp}',CH1)
np.save(f'{sys.argv[2]}_{timestamp}',CH2)
print("\nend of demonstration")

