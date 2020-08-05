import pyvisa
import re
import threading
import time

def stopScope(scope):
    scope.write("ACQ:STATE OFF")
    print("STOP Function ran at time: " + str(int(time.time())) + " seconds.")


def startScope(scope):
    scope.write("ACQ:STATE ON")
    print("START Function ran at time: " + str(int(time.time())) + " seconds.")

rm = pyvisa.ResourceManager()
scope1 = rm.open_resource('TCPIP::192.168.1.2::INSTR')
scope2 = rm.open_resource('TCPIP::192.168.1.3::INSTR')

threading.Thread(target=startScope(scope1)).start()
threading.Thread(target=startScope(scope2)).start()
time.sleep(1.5)
threading.Thread(target=stopScope(scope1)).start()
threading.Thread(target=stopScope(scope2)).start()

scope1.close()
scope2.close()
rm.close()
