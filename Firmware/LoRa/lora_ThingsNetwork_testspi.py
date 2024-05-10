from machine import SPI, Pin
import time
import struct
import sys

# Define SPI pins
SPI_ID = 0
SCK_PIN = 2
MOSI_PIN = 3
MISO_PIN = 4
NSS_PIN = 1

# TTN parameters
app_key = '88A05B55578DEEAC481105C99A6AFA36'  # AppKey obtained from TTN
band = 'EU868'  # LoRaWAN band setting
channels = '0-2'  # LoRaWAN channel settings

# Device and Join EUIs
dev_eui = '5695130620360003000'  # Device EUI
join_eui = '655848791746576400'  # Join EUI

# Initialize SPI
spi = SPI(SPI_ID, baudrate=5000000, polarity=0, phase=0, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN), miso=Pin(MISO_PIN))

### Function Definitions

def send_AT(command):
    '''Wraps the "command" string with AT+ and \r\n and sends it via SPI'''
    # Start SPI transaction
    cs = Pin(NSS_PIN, Pin.OUT)
    cs.value(0)

    # Send command
    command = 'AT' + command + '\r\n'
    spi.write(bytearray(command, 'utf-8'))

    # End SPI transaction
    cs.value(1)

    time.sleep_ms(300)

def configure_regional_settings(band, channels):
    ''' Configure LoRaWAN regional settings'''
    send_AT('+DR=' + band)
    send_AT('+CH=NUM,' + channels)
    send_AT('+MODE=LWOTAA')

    print("Configured regional settings.")

def join_the_things_network():
    '''Connect to The Things Network. Exit on failure'''
    send_AT('+JOIN')

    print("Joining The Things Network...")

    status = 'not connected'
    start_time = time.ticks_ms()
    while status == 'not connected':
        data = receive_spi()
        data_str = data.decode('utf-8')
        if len(data_str) > 0:
            print(data_str)
            if 'joined' in data_str.split():
                status = 'connected'
                print("Join successful!")
            elif 'failed' in data_str.split():
                print('Join Failed')
                sys.exit()  # Exit the script
                
        # Check if it's been too long without a response
        if time.ticks_diff(time.ticks_ms(), start_time) > 30000:  # 30 seconds timeout
            print("Join process timed out.")
            sys.exit()  # Exit the script
            
        time.sleep_ms(1000)

def send_message(message):
    '''Send a string message'''
    send_AT('+MSG="' + message + '"')

    print("Sending message:", message)

    done = False
    while not done:
        data = receive_spi()
        data_str = data.decode('utf-8')
        if 'Done' in data_str or 'ERROR' in data_str:
            done = True
        if len(data_str) > 0:
            print(data_str)

def send_hex(message):
    '''Send a hexadecimal message'''
    send_AT('+MSGHEX="' + message + '"')

    print("Sending hexadecimal message:", message)

    done = False
    while not done:
        data = receive_spi()
        data_str = data.decode('utf-8')
        if 'Done' in data_str or 'ERROR' in data_str:
            done = True
        if len(data_str) > 0:
            print(data_str)

def receive_spi():
    '''Receive data via SPI'''
    # Start SPI transaction
    cs = Pin(NSS_PIN, Pin.OUT)
    cs.value(0)

    # Send dummy data to trigger response
    spi.write(bytearray([0x00]))

    # Receive response
    response = spi.read(64)  # Adjust the buffer size as per your expected response size

    # End SPI transaction
    cs.value(1)

    return response

##########################################################
#        
# The main program starts here
#
##########################################################

# Configure LoRaWAN regional settings
configure_regional_settings(band, channels)

# Set device EUI and join EUI
send_AT('+ID=DevEui,' + dev_eui)
send_AT('+ID=AppEui,' + join_eui)

# Join The Things Network
join_the_things_network()

# Send example data
print("Sending test messages")
send_message("Hello World!")
send_hex("00112233445566778899AABBCCDDEEFF")

print("Test messages sent.")
