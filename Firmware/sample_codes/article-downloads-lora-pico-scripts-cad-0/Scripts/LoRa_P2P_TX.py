# P2P Transmitter Example
# Transmit test data direct to another Makerverse LoRa Breakout

from machine import UART, Pin
from utime import sleep_ms

uart1 = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

def echo():
    rxData=bytes()
    while uart1.any()>0:
        rxData += uart1.read(1)
    print(rxData.decode('utf-8'))

uart1.write('at+mode=test\n')  # enter test mode
sleep_ms(100)

data = 0

while True:   
    print("Send data:",data)
    uart1.write('at+test=txlrpkt,"{}"\n'.format(data))  # send test data
    sleep_ms(100)
    
    echo() # show debug data from LoRa-E5 module
    
    data += 1 # increment and loop test-data
    data = data % 255
    
    print("")
    sleep_ms(1000)