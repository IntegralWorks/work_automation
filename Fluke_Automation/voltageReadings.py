#TO-DO: THREADING!
import pyvisa as visa
import sys, csv

#https://electronics.stackexchange.com/questions/249531/reading-a-number-of-voltage-samples-with-fluke-8845a
#NOTE: There is NO substitute for the Fluke 8845A Programmer's Manual. The Tektronix one(s) help too.

#call it like this: py automatedFluke.py csvFilename leftMeter rightMeter 0,1,2,3,5,10

def generateFields():
    l = []
    for i in sys.argv[-1].split(','):
        """
        what this does is take a comma-delimited string at the end of the system argument vector
        and convert into a list. So if you say 
        py automatedFluke.py csvFilename leftMeter rightMeter testA,testB,testC
        the script will direct the meters to take 3 measurements, each corresponding to that label--
        this means there will be 6 columns, with each meter having its iteration of each label.
        the reason taking these samples is semi manual (pressing the enter button) is because
        this script is mostly for automating feedback measurements, with the idea being that
        you can stuff either a repetitive or comprehensive feedback test in one spreadsheet
        by setting this script up, coming up with a name for each test,
        and then looping your work by
        setting up the circuit --> taking sample --> setting up the circuit --> taking sample

        TO-DO: figure out:
            A) how to take more than 100 sample points at a time
            B) how to space out the sample points if necessary
            C) make getVoltageValues(...) accept system arguments
            D) use LAN instead of serial (perhaps)
        """
        l.append(f'{sys.argv[2]+i}')
        l.append(f'{sys.argv[3]+i}')
    return l

fields = generateFields()

rm = visa.ResourceManager()

leftMeter = rm.open_resource('ASRL9::INSTR')
leftMeter.baud_rate  = 115200
leftMeter.timeout  = 100000
rightMeter = rm.open_resource('ASRL4::INSTR')
rightMeter.baud_rate  = 115200
rightMeter.timeout  = 100000

def getVoltageValues(inst):
    inst.write('*cls')
    inst.write('*rst')
    inst.write('conf:volt:dc .500') 
    inst.write('volt:dc:nplc 1') #set significant figures with the values [0.02, 0.2, 1, 10, 100] the higher, the more sig-figs but the slower the sampling is
    inst.write('zero:auto 0')
    inst.write('trig:sour imm')
    inst.write('trig:del 0')
    inst.write('trig:coun 1') #if you change '1' with some int n, you will get n*100 record points -- at the cost of speed
    inst.write('syst:rem')
    inst.write('samp:coun 100') #don't mess with this without consulting the manual
    inst.write(':INIT')
    inst.query('*OPC?')
    #inst.query(':FETCH?')

def fetchValues(inst1,inst2,n,fields):
    fields = fields
    values = {}
    counter = 0
    flag = False
    print(f'fetchValues(..) called. Commencing SCPI commands. Counter: {counter}')
    while flag != True:
        getVoltageValues(inst1)
        getVoltageValues(inst2)

        values[fields[counter]] = inst1.query('fetch?').replace('\r\n','').split(',')
        counter+=1
        values[fields[counter]] = inst2.query('fetch?').replace('\r\n','').split(',')
        counter+=1
        print(f'counter before: {counter} after: {counter}')

        if counter==n or counter>n:
            print(f'Done fetching values at counter value: {counter}')
            flag = True

        input('press enter when the next set of voltage values are ready\n')
        
    return values

values = fetchValues(leftMeter, rightMeter, len(fields), fields)

def writeCsv(d, fields):
    keys = fields
    with open(f'{sys.argv[1]}.csv', "w", newline='') as outfile:
        writer = csv.writer(outfile, delimiter = ",")
        writer.writerow(keys)
        writer.writerows(zip(*[d[key] for key in keys]))
        #the * operator within function calls unpacks data structures such as lists into arguments.
        #so you can create many arguments on the fly with a list comphrehension.

writeCsv(values,fields)
