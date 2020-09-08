import pyvisa as visa
import sys
from datetime import datetime, date, timedelta
visa_address = 'TCPIP0::169.254.8.227::inst0::INSTR'

rm = visa.ResourceManager()
scope = rm.open_resource(visa_address)

timestamp = datetime.now()
date = timestamp.strftime('%x').replace('/','-')
time = timestamp.strftime('%X').replace(':','.')

f = open(f'{date}_{time}_backupSettings.txt','w')
f.write(scope.query(f'ch1:label?'))
f.write(scope.query(f'ch1:scale?'))
f.write(scope.query(f'ch2:label?'))
f.write(scope.query(f'ch2:scale?'))
f.write(scope.query(f'ch3:label?'))
f.write(scope.query(f'ch3:scale?'))
f.write(scope.query(f'ch4:label?'))
f.write(scope.query(f'ch4:scale?'))
f.close()

if sys.argv[1] == '-s' or sys.argv[1] == '-simple':
    print('feature not implemented yet')
    #eventually
elif sys.argv[1] == '-l' or sys.argv[1] == '-load':
    f2 = open(f'{sys.argv[2]}', 'r')
    newlineChar = "\n"
    scope.write(f'ch1:label {f2.readline().replace(newlineChar,"")}')
    scope.write(f'ch1:scale {f2.readline().replace(newlineChar,"")}')
    scope.write(f'ch2:label {f2.readline().replace(newlineChar,"")}')
    scope.write(f'ch2:scale {f2.readline().replace(newlineChar,"")}')
    scope.write(f'ch3:label {f2.readline().replace(newlineChar,"")}')
    scope.write(f'ch3:scale {f2.readline().replace(newlineChar,"")}')
    scope.write(f'ch4:label {f2.readline().replace(newlineChar,"")}')
    scope.write(f'ch4:scale {f2.readline().replace(newlineChar,"")}')
    f2.close()
else:
#arguments go as {label voltageScaling}
#therefore py thiscript.py -arg labelCH1 vScalingCH1 labelCH2 vScalingCH2 ...
    scope.write(f'ch1:label "{sys.argv[2]}"')
    scope.write(f'ch1:scale {sys.argv[3]}')
    scope.write(f'ch2:label "{sys.argv[4]}"')
    scope.write(f'ch2:scale {sys.argv[5]}')
    scope.write(f'ch3:label "{sys.argv[6]}"')
    scope.write(f'ch3:scale {sys.argv[7]}')
    scope.write(f'ch4:label "{sys.argv[8]}"')
    scope.write(f'ch4:scale {sys.argv[9]}')
