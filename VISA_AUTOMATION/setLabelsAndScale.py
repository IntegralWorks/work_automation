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

#Note: violated the DRY principle for better performance. I don't really recommend refactoring
#to a for loop where you specify which channels to change because it really is faster this way.
#but I do recognize not to code like this 99% of the time.
if sys.argv[1] == '-s' or sys.argv[1] == '-simple':
    scope.write(f'ch1:label "{input("Type CH1 label: ")}" ')
    scope.write(f'ch1:scale {input("Type CH1 voltage scale: ")} ')
    scope.write(f'ch2:label "{input("Type CH2 label: ")}" ')
    scope.write(f'ch2:scale {input("Type CH2 voltage scale: ")} ')
    scope.write(f'ch3:label "{input("Type CH3 label: ")}" ')
    scope.write(f'ch3:scale {input("Type CH3 voltage scale: ")} ')
    scope.write(f'ch4:label "{input("Type CH4 label: ")}" ')
    scope.write(f'ch4:scale {input("Type CH4 voltage scale: ")} ')

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

scope.close()
rm.close()
