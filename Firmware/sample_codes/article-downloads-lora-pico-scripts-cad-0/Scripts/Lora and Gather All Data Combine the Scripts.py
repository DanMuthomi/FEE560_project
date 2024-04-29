#LoRaWAN Trasmition of Weather Data Gathered By a Rasperry Pi Pico

#Below Section is the Script to get the Raspberry Pi Pico to Collect Data from the Weather Sensors 

# Read air quality metrics from the PiicoDev Air Quality Sensor ENS160 and PiicoDev Atmospheric Sensor BME280
# ENS160 Shows three metrics: AQI, TVOC and eCO2
# ENS160 also shows Sensor Operational Mode (has it recorded for a while or just started recording (less accurate))
# BME280 Shows three metrics: Temperature, Pressure and Humidity
# All data gets compiled into a single string and sent through UART to be Read and Transmitted through LORA to a Gateway to be Displayed on The Things Network.

# Import the device driver ENS160 (defaults to i2C Address 0x53 (ASW Switch in OFF position), identical to | "PiicoDev_ENS160(address=0x53)" |)
from PiicoDev_ENS160 import PiicoDev_ENS160

# Import the device driver BME280 (defaults to i2C Address 0x77 (ASW Switch in OFF position), identical to | "PiicoDev_BME280(address=0x77)" |)
from PiicoDev_BME280 import PiicoDev_BME280

# Import the PiicoDev cross-platform sleep function
from PiicoDev_Unified import sleep_ms       

# Import UART to send data to LORA Antenna and LED Light Controls
from machine import Pin
from machine import UART

# Initialise a Variable for the on board LED to provide Feedback 
led = machine.Pin('LED', machine.Pin.OUT)

# Initialise the communication location and Baud Rate for communicating through UART to the LORA Trasmitter <------------------------------------Probably Not 0!
uart = UART(0, 9600)

# Initialise a Variable for the ENS160 module
sensor1 = PiicoDev_ENS160()

# Initialise a Variable for the BME280 module
sensor2 = PiicoDev_BME280()   

#zeroAlt = sensor.altitude() # take an initial altitude reading for BME280

# Start an Endless Loop, Everything indented below (thus inside the | while True: | statement) will repeat forever.
#while True:


#--------------------------------------------------------------------------------------
# Warm Up Read from Sensor 1 (ENS160)
aqi = sensor1.aqi
tvoc= sensor1.tvoc
eco2 = sensor1.eco2

sleep_ms(1000)

#True Read from Sensor 1 (ENS160)
aqi = sensor1.aqi
tvoc = sensor1.tvoc
eco2 = sensor1.eco2

# Print air quality metrics from Sensor 1 (ENS160)

print('Air Quality Sensor')
print('   AQI: ' + str(aqi.value) + ' [' + str(aqi.rating) +']')
print('   TVOC: ' + str(tvoc) + ' ppb')
print('   eCO2: ' + str(eco2.value) + ' ppm [' + str(eco2.rating) +']')
print('Operational Mode Status: ' + str(sensor1.operation))

print('--------------------------------')

# Small timeout to avoid spamming shell
sleep_ms(1000)

# Warm Up Read Weather Data Metrics from Sensor 2 (BME280)

tempC, presPa, humRH = sensor2.values()

sleep_ms(1000)

#True Read Weather Data Metrics from Sensor 2 (BME280)

tempC, presPa, humRH = sensor2.values()

# Convert air pressure Pascals -> hPa (or mbar, if you prefer)

pres_hPa = presPa / 100


#Provide + or - Symbol Representation for Temperature. 1 = Positive Symbol. 2 = Negative Symbol
if tempC >= 0:
    x = 1
if tempC < 0:
    x = 2


#Removing Decimal Points from Data
#Removing Dot Points from Data whilst Maintaining the integrity of the information to lower Byte Size.
CleanTemperature = abs((int(tempC*100)))
#print(CleanTemperature)
CleanPressure = int((pres_hPa*100))
#print(CleanPressure)
CleanHumidity = (int(humRH*100))
#print(CleanHumidity)


#Add back 0 Prefixes to Maintain Integrity of Data in all scenarios
#ZeroedCleanTemperature = "{:4d}".format(int(CleanTemperature))
#ZeroedCleanPressure = "{:6d}".format(int(CleanPressure))
#ZeroedCleanHumidity = "{:5d}".format(int(CleanHumidity))
#ZeroedTVOC = "{:5d}".format(int(tvoc))
#ZeroedC02 = "{:5d}".format(int(eco2.value))

ZeroedCleanTemperature = str((f" {CleanTemperature : 05d} "))
ZeroedCleanPressure = str((f" {CleanPressure : 07d} "))
ZeroedCleanHumidity = str((f" {CleanHumidity : 06d} "))
ZeroedTVOC = str((f" {tvoc : 06d} "))
ZeroedC02 = str((f" {eco2.value : 06d} "))


# Print Weather Metrics from Sensor 2 (BME280)

print('Atmospheric Weather Sensor')
print('   Temperture: ' + str(tempC)+' °C')
print('   Pressure: ' + str(pres_hPa)+' hPa')
print('   Humidity: ' + str(humRH)+' %Relative Humidity')

print('--------------------------------')


# Small timeout to avoid spamming shell
sleep_ms(1000)

print('Showing Data Segmented Cleaned and Zeroed, Dot Points Removed')

print(x)
print(ZeroedCleanTemperature)
print(ZeroedCleanPressure)
print(ZeroedCleanHumidity)
print(ZeroedTVOC)
print(ZeroedC02)

sleep_ms(1000)

# Send All Data through the connected LORA device as a small String Packet. Start by Compiling All Data into a Single String
All_Data = str(x) + (ZeroedCleanTemperature) + (ZeroedCleanPressure) + (ZeroedCleanHumidity) + str(aqi.value) + (ZeroedTVOC) + (ZeroedC02) #+ ',' + str(sensor1.operation)
#All_Data = '- Temperture ' + str(tempC) + ' °C \n- Pressure ' + str(pres_hPa) + ' hPa \n- Humidity ' + str(humRH) + ' %Relative Humidity \n- Air Quality Index ' + str(aqi.value) + ' - [' + str(aqi.rating) + ']' + '\n- TVOC ' + str(tvoc) + ' ppb \n- eCO2 ' + str(eco2.value) + 'ppb - [' + str(eco2.rating) + ']'
#All_Data = str(ONEDP_tempC) + '°C-' + str(ONEDP_pres_hPa) + 'hPa-' + str(ONEDP_humRH) + '%RH-' + str(aqi.value) + 'AQI-' + str(tvoc) + 'VOC-' + str(eco2.value) + 'CO2'

print('--------------------------------')

print('Collating Data into One String')
#print all data
print(All_Data)
print('--------------------------------')

sleep_ms(1000)

print('Cleaned Data Packet Ready for Transmission')
Final_All_Data = All_Data.replace(" ", "")
print(Final_All_Data)

print('--------------------------------')
print('--------------------------------')
    
#--------------------------------------------------------------------------------------------    
    
    
#Provide some feedback with LED Blinking for Troubleshooting Purposes
led.on()
sleep_ms(200)
led.off()
sleep_ms(200)
led.on()
sleep_ms(200)
led.off()
sleep_ms(200)
led.on()
sleep_ms(200)
led.off()
sleep_ms(200)
led.on()
sleep_ms(1000)
led.off()

    
# Put your key here (string). This should match the AppKey generated by your application.
#For example: app_key = 'E08B834FB0866939FC94CDCC15D0A0BE'
app_key = None

#Placed My Generated AppKey Here
app_key = 'AAC1F35E1B70F59EFB201F231B7D7B60'


# Regional LoRaWAN settings. You may need to modify these depending on your region.
# If you are using AU915: Australia
band='AU915'
channels='8-15'

# If you are using US915
# band='US915'
# channels='8-15'
# 
# If you are using EU868
# band='EU868'
# channels='0-2'




from machine import UART, Pin
from utime import sleep_ms
from sys import exit

uart1 = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
join_EUI = None   # These are populated by this script
device_EUI = None

### Function Definitions

def receive_uart():
    '''Polls the uart until all data is dequeued'''
    rxData=bytes()
    while uart1.any()>0:
        rxData += uart1.read(1)
        sleep_ms(2)
    return rxData.decode('utf-8')

def send_AT(command):
    '''Wraps the "command" string with AT+ and \r\n'''
    buffer = 'AT' + command + '\r\n'
    uart1.write(buffer)
    sleep_ms(300)

def test_uart_connection():
    '''Checks for good UART connection by querying the LoRa-E5 module with a test command'''
    send_AT('') # empty at command will query status
    data = receive_uart()
    if data == '+AT: OK\r\n' : print('LoRa radio is ready\n')
    else:
        print('LoRa-E5 detected\n')
        exit()

def get_eui_from_radio():
    '''Reads both the DeviceEUI and JoinEUI from the device'''
    send_AT('+ID=DevEui')
    data = receive_uart()
    device_EUI = data.split()[2]

    send_AT('+ID=AppEui')
    data = receive_uart()
    join_EUI = data.split()[2]

    print(f'JoinEUI: {join_EUI}\n DevEUI: {device_EUI}')
    
def set_app_key(app_key):
    if app_key is None:
        print('\nGenerate an AppKey on cloud.thethings.network and enter it at the top of this script to proceed')
        exit()

    send_AT('+KEY=APPKEY,"' + app_key + '"')
    receive_uart()
    print(f' AppKey: {app_key}\n')


def configure_regional_settings(band=None, DR='0', channels=None):
    ''' Configure band and channel settings'''
    
    send_AT('+DR=' + band)
    send_AT('+DR=' + DR)
    send_AT('+CH=NUM,' + channels)
    send_AT('+MODE=LWOTAA')
    receive_uart() # flush
    
    send_AT('+DR')
    data = receive_uart()
    print(data)


def join_the_things_network():
    '''Connect to The Things Network. Exit on failure'''
    send_AT('+JOIN')
    data = receive_uart()
    print(data)

    status = 'not connected'
    while status == 'not connected':
        data = receive_uart()
        if len(data) > 0: print(data)
        if 'joined' in data.split():
            status = 'connected'
        if 'failed' in data.split():
            print('Join Failed')
            exit()
        
        sleep_ms(1000)
        
def send_message(message):
    '''Send a string message'''
    send_AT('+MSG="' + message + '"')

    done = False
    while not done:
        data = receive_uart()
        if 'Done' in data or 'ERROR' in data:
            done = True
        if len(data) > 0: print(data)
        sleep_ms(1000)
        
def send_hex(message):
    send_AT('+MSGHEX="' + message + '"')

    done = False
    while not done:
        data = receive_uart()
        if 'Done' in data or 'ERROR' in data:
            done = True
        if len(data) > 0: print(data)
        sleep_ms(1000)



##########################################################
#        
# The main program starts here
#
##########################################################

test_uart_connection()

get_eui_from_radio()

set_app_key(app_key)

configure_regional_settings(band=band, DR='0', channels=channels)

join_the_things_network()

#Send Current Weather Data represented by All_Data through UART to the attached LORA Device to Transmit to the Gateway
    
print("Sending Current Weather Data String Through LoRa!")
send_message(Final_All_Data)
#send_hex("00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF")


    