# P2P Receiver Example
# Receive test data from another Makerverse LoRa Breakout

from machine import UART, Pin
from utime import sleep_ms

uart1 = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

def echo():
    rxData=bytes()
    while uart1.any()>0:
        rxData += uart1.read(1)
    data = rxData.decode('utf-8')
    out = data.replace('+TEST: RXLRPKT','')
    print(out)

uart1.write('at+mode=test\n')  # enter test mode
sleep_ms(100)

while True:   
    uart1.write('at+test=rxlrpkt\n')

    echo() # show debug data from LoRa-E5 module
    
    sleep_ms(1000)