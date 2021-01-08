import pyvisa as visa
import PySimpleGUI as sg
import re, sys, os
from io import BytesIO
import win32clipboard
from PIL import Image, ImageTk
import base64
import time
import xlsxwriter as excel
import datetime as dt
import string
import pretty_errors
import csv
import numpy as np

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

def fetch_base64Image(inst=scope,placeholder=False):
    buffered = BytesIO()
    if placeholder == False:
        inst.write('SAVE:IMAGE:FILEF png')
        inst.write('HARDCOPY START')
        raw_data = inst.read_raw()
        im = Image.open(BytesIO(raw_data))
        im.save(buffered, format='PNG')
        img_str = base64.b64encode(buffered.getvalue())
    else:
        placeholder = Image.new('RGB',(1,1), (255, 255, 255))
        placeholder.save(buffered, format='PNG')
        img_str = base64.b64encode(buffered.getvalue())
    return img_str

def decodeAndConvert_base64String(b64_str, memory_mode = False):
    image = Image.open(BytesIO(base64.b64decode(b64_str)))
    if memory_mode == False:
        return ImageTk.PhotoImage(image)
    if memory_mode == True:
        buffered = BytesIO()
        image.save(buffered, format='PNG')
        return buffered

def export(ims, m):
    workbook = excel.Workbook('proof_of_concept.xlsx')
    worksheet = workbook.add_worksheet('lol')
    x = 0
    y = 0
    for n,i in enumerate(ims):
        worksheet.insert_image(x, y, 'dummy.png', {'image_data' : decodeAndConvert_base64String(i, True)})
        xcopy = x
        ycopy = y
        ycopy+=13
        for v in m[n]:
            # if ycopy ==12:
            #     ycopy = 13
            worksheet.write_row(xcopy, ycopy, v)
            xcopy+=1
        x += 26
        if x >= 78:
            y += 16
            x = 0
    workbook.close()

def increment(a, t, incr):
    scope.write(f'cursor:vbars:position{a} {np.float(t)+incr}')
    scope.write('*cls')
    time.sleep(.350)

def resetScrolling():
    scope.write(f'zoom:zoom1:position 0.0' )
    time.sleep(.500)
    scope.write('*cls')

def scroll():
    scope.write('mark next')
    scope.write('*cls')
    time.sleep(.500)
    scope.write(f'zoom:zoom1:position {scope.query("mark:selected:focus?")}' )
    time.sleep(.500)
    scope.write('*cls')

def setMeasurementChannel(source, CH):
    scope.write(f'measurement:immed:source{source} {CH}')
    scope.write('*cls')
    time.sleep(.100)


def takeMeasurement(meas_type, n_ch, CH_A='CH1', CH_B='CH2'):
    if n_ch == 1:
        scope.write(f'measurement:immed:type {meas_type}')
        scope.write('*cls')
        time.sleep(.100)
        v = scope.query('measurement:immed:value?')
        scope.write('*cls')
        time.sleep(.100)
        return (meas_type , v)
    if n_ch == 2:
        if lower(meas_type) == 'delay':
            scope.write(f'measurement:immed:source2 {CH_B}')
            scope.write(f'measurement:immed:{meas_type}')
            v1 = scope.query('measurement:immed:value?')
            scope.write('*cls')
            time.sleep(.100)
            scope.write(f'measurement:immed:source1 {CH_B}')
            scope.write(f'measurement:immed:source2 {CH_A}')
            v2 = scope.query('measurement:immed:value?')
            scope.write('*cls')
            time.sleep(.100)
            setMeasurementChannel(1, "CH1")
            return (meas_type+f'{CH_A},{CH_B};{CH_A},{CH_B}', (v1,v2))




# def scroll():
#     positions = range(1, int(scope.query('mark:total?')))
#     scope.write(f'zoom:zoom1:position 0.0' )
#     time.sleep(.500)
#     scope.write('*cls')
#     scope.write('mark next')
#     scope.write('*cls')
#     time.sleep(.500)
#     for i in range(1, int(scope.query('mark:total?'))):
#         scope.write(f'zoom:zoom1:position {scope.query("mark:selected:focus?")}' )
#         time.sleep(.500)
#         scope.write('*cls')
#         scope.write('mark next')
#         time.sleep(.500)
#         scope.write('*cls')

def seekCursor1Cross(targetPattern):
    scope.write('*cls')
    value = float(re.match(targetPattern, scope.query('cursor:vbars?')).group(4))
    print(f"CURSOR A: {value}")
    if value == 0.0:
        scope.write('*cls')
        time.sleep(.150)
        return False
    else:
        return True
    scope.write('*cls')

def seekCursor2Cross(targetPattern):
    scope.write('*cls')
    value = float(re.match(targetPattern, scope.query('cursor:vbars?')).group(5))
    print(f"CURSOR B: {value}")
    if value == 0.0:
        scope.write('*cls')
        time.sleep(.350)
        return False
    else:
        return True
    scope.write('*cls')

def findCrosses():
    setMeasurementChannel(1, 'CH1')
    resetScrolling()
    l = []
    measurements = []
    scope.write('*CLS')
    scope.write('SEARCH:SEARCH1:STATE ON')
    scope.write(f'SEARCH:SEARCH1:TRIGger:A:LEVel:CH1 0')
    statusPattern = '(.*);(.*);(.*);(.*);(.*);(.*)(.*);(.*);(.*);(.*);(.*)'
    #Confirms that the search is done
    while(re.match(statusPattern, scope.query('mark?')).group(11) == '0'):
        pass
    valuePattern = '(.*),(.*),(.*),(.*),(.*),(.*)(.*),(.*),(.*)'
    scope.write('mark:saveall touser')
    initialValues = []
    for i in scope.query('mark:userlist?').split(';'):
        initialValues.append(np.float(re.match(valuePattern,i).group(5)))
    toggle = True
    incr = 1e-6
    successfulValues = []
    targetPattern = '(.*);(.*);(.*);(.*);(.*);(.*);(.*)'
    status = 0
    meas_types = ['RMS', 'Frequency']
    for n in range(1, int(scope.query('mark:total?'))):
        scroll()
        cur1Status = True
        cur2Status = False
        meas = []
        while cur1Status:
            increment(1, initialValues[n-1], incr)
            if not seekCursor1Cross(targetPattern):
                cur1Status = False
                break
            increment(1, initialValues[n-1], -incr)
            cur1Status = seekCursor1Cross(targetPattern)
            incr+=10e-7
            if (incr >= 2e6 ):
                if meta == 1:
                    incr = 1.1e-6
                    meta = 0
                incr = .9e-6
                meta = 1
        cur2Status = True
        incr = 1e-6
        while cur2Status:
            increment(2, initialValues[n], incr)
            if not seekCursor2Cross(targetPattern):
                cur2Status = False
                break
            increment(2, initialValues[n], -incr)
            cur2Status = seekCursor2Cross(targetPattern)
            incr+=10e-7
            if (incr >= 2e6 ):
                if meta == 1:
                    incr = 1.1e-6
                    meta = 0
                incr = .9e-6
                meta = 1
        cur1Status = True
        incr = 1e-6
        print('Crosses Found. Screenshotting!')
        l.append(fetch_base64Image())
        meas.append(takeMeasurement(meas_types[0],1))
        meas.append(takeMeasurement(meas_types[1],1))
        measurements.append(meas)
    scope.write('SEARCH:SEARCH1:STATE OFF')
    return l, measurements

ims, m = findCrosses()
export(ims, m)
