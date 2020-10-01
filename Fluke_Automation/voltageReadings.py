import pyvisa as visa
import sys, string, csv
from time import sleep
#https://electronics.stackexchange.com/questions/249531/reading-a-number-of-voltage-samples-with-fluke-8845a

rm = visa.ResourceManager()

topMeter = rm.open_resource('ASRL6::INSTR')
bottomMeter = rm.open_resource('ASRL4::INSTR')

def getVoltageValues(inst):
    inst.write('*cls')
    inst.write('*rst')
    inst.write('conf:volt:dc .5')
    inst.write('volt:dc:nplc 0.03')
    inst.write('zero:auto 0')
    inst.write('trig:sour imm')
    inst.write('trig:del 0')
    inst.write('trig:coun 1')
    inst.write('syst:rem')
    inst.write('samp:coun 100')
    inst.write(':INIT')
    inst.query('*OPC?')
    #inst.query(':FETCH?')

#first you call getVoltageValues(inst_referenced).
#then you call A = inst_referenced.query('fetch')
#rinse and repeat, Until you get your A,B,C...whenever.

def fetchValues(inst1,inst2,n):
    fields = sys.argv[2:]
    values = {}
    counter = 0
    flag = False
    print(f'fetchValues(..) called. Commencing SCPI commands. Counter: {counter}')
    while flag != True:
        getVoltageValues(inst1)
        sleep(.001)
        getVoltageValues(inst2)

        values[fields[counter]] = inst1.query('fetch?').replace('\r\n','').split(',')
        counter+=1
        values[fields[counter]] = inst2.query('fetch?').replace('\r\n','').split(',')
        counter+=1
        print(f'counter before: {counter} after: {counter}')

        if counter==n:
            print(f'Done fetching values at counter value: {counter}')
            flag = True

        input('press enter when the next set of voltage values are ready\n')
        
    return values

values = fetchValues(topMeter, bottomMeter, len(sys.argv[2:]))

def writeCsv(d):
    keys = sys.argv[2:]
    with open(f'{sys.argv[1]}.csv', "w", newline='') as outfile:
        writer = csv.writer(outfile, delimiter = ",")
        writer.writerow(keys)
        writer.writerows(zip(*[d[key] for key in keys]))

writeCsv(values)
