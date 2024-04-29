# P2P Transmitter Example
# Transmit test data direct to another Makerverse LoRa Breakout

from machine import UART, Pin
from utime import sleep_ms

uart1 = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5), rxbuf=128)


def echo():
    rxData=bytes()
    while uart1.any()>0:
        rxData += uart1.read(1)
    print(rxData.decode('utf-8'))

def AT(command):
    uart1.write('AT+' + command + '\n')

uart1.write('AT\n')
sleep_ms(100)
echo()

uart1.write('at+mode=test\n')
sleep_ms(100)
echo()

uart1.write('AT+DR=0\n')
sleep_ms(100)
echo()

uart1.write('AT+DR?\n')
sleep_ms(100)
echo()


# AT('mode=test\n')  # enter test mode

uart1.write('AT+CH\n')
sleep_ms(100)
echo()

