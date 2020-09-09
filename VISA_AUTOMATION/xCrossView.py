import pyvisa as visa
import sys
import time
import pandas as pd
ip = 'TCPIP0::169.254.8.227::inst0::INSTR'
rm = visa.ResourceManager()
scope = rm.open_resource(ip)

def zeroCross(CH, value=0, slope='either'):
    CH_list = ['CH1', 'CH2', 'CH3', 'CH4']
    CH_list.pop(CH_list.index(f'{CH}'))
    scope.write(f'select:{CH_list[0]} 1')
    scope.write(f'select:{CH_list[1]} 1')
    scope.write(f'select:{CH_list[2]} 1')
    scope.write(f'select:{CH} 1')
    CH_list.append(CH)
    scope.write(f':SEARCH:SEARCH1:TRIGger:A:EDGE:SOUrce {CH}')
    scope.write(f':SEARCH:SEARCH1:TRIGger:A:LOWerthreshold:{CH} {float(value)}')
    scope.write(f':SEARCH:SEARCH1:TRIGger:A:EDGE:SLOpe {slope}')
    scope.write(f':SEARCH:SEARCH1:STATE 1')

zeroCross(*sys.argv[1:4])

scope.close()
rm.close()
