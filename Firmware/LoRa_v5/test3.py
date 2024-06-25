import utime
import struct
import urandom
import ujson
from sx127x import TTN, SX127x
from machine import Pin, SPI, ADC
from config import *

# Define soil moisture sensor and water pump pins
soil = ADC(Pin(26))  # Soil moisture sensor ADC pin
pump = Pin(15, Pin.OUT)  # Relay activation pin
irrigON = Pin(20, Pin.OUT) # LED to indicate when irrigation is happening
moistureOK = Pin(19, Pin.OUT) # LED showing good soil conditions

# Calibration values for soil sensor ADC readings
min_moisture = 0
max_moisture = 65535
pump_on_threshold = 20.0
pump_off_threshold = 50.0

read_delay = 5  # Time between readings

# Pump flow rate in liters per minute (L/min)
pump_flow_rate = 10 # quivalent to 600L/H

# Setting pico debug pin
__DEBUG__ = True

# Initiating saved frame counters for lora reception (lora security measure)
FRAME_COUNTER_FILE = 'frame_counter.txt'

def save_frame_counter(counter):
    with open(FRAME_COUNTER_FILE, 'w') as f:
        f.write(str(counter))

def load_frame_counter():
    try:
        with open(FRAME_COUNTER_FILE, 'r') as f:
            return int(f.read())
    except OSError:
        return 0

# Setting server access configurations
ttn_config = TTN(ttn_config['devaddr'], ttn_config['nwkey'], ttn_config['app'], country=ttn_config['country'])

# Initiating SPI pins
device_spi = SPI(device_config['spi_unit'], baudrate = 10000000, 
        polarity = 0, phase = 0, bits = 8, firstbit = SPI.MSB,
        sck = Pin(device_config['sck'], Pin.OUT, Pin.PULL_DOWN),
        mosi = Pin(device_config['mosi'], Pin.OUT, Pin.PULL_UP),
        miso = Pin(device_config['miso'], Pin.IN, Pin.PULL_UP))

# Initiating lora device connected to SPI0
lora = SX127x(device_spi, pins=device_config, lora_parameters=lora_parameters, ttn_config=ttn_config)
frame_counter = load_frame_counter()

# lora callback function
def on_receive(lora, outgoing):
    payload = lora.read_payload()
    print(payload)

lora.on_receive(on_receive)
lora.receive()

# Soil sensor reading function
def read_moisture():
    moisture_adc = soil.read_u16()
    moisture = (max_moisture - moisture_adc) * 100 / (max_moisture - min_moisture)
    return moisture, moisture_adc

# Main loop function
def main():
    frame_counter = load_frame_counter()
    while True:
        # Resetting local variables to zero
        initial_moisture = None
        pump_duration = None
        final_moisture = None
        
        # Calling read sensor function
        moisture, moisture_adc = read_moisture()
        print(f"moisture: {moisture:.2f}% (adc: {moisture_adc})")
        
        # Checking sensor readin to lower end threshold
        if moisture < pump_on_threshold:
            initial_moisture = moisture
            pump.value(1)  # Turn on the pump
            irrigON.value(1) # Turning on irrigation indicator LED
            moistureOK.value(0) # Turning off moisture ok indicator LED
            start_time = utime.time() #Starting pump timer
            print("Pump turned on.")
            
            # Monitoring sensor values against upper moisture threshold
            while moisture < pump_off_threshold:
                utime.sleep(read_delay)
                moisture, moisture_adc = read_moisture()
                print(f"moisture: {moisture:.2f}% (adc: {moisture_adc})")
                
            # Code once while loop becomes false
            pump.value(0)  # Turn off the pump
            irrigON.value(0) # Turning off irrigation indicator LED
            moistureOK.value(1) # Turning on moisture ok indicator LED
            pump_duration = utime.time() - start_time  # Duration in seconds
            final_moisture = moisture # Setting final sensor reading value
            print("Pump turned off.")
                    
            # Calculate the amount of water used
            pump_duration_minutes = pump_duration / 60  # Convert duration to minutes
            water_used = pump_duration_minutes * pump_flow_rate  # Water used in liters
                    
            # Prepare message packet
            message = {
                "initial_moisture": initial_moisture,
                "pump_duration": pump_duration,
                "water_used": water_used,
                "final_moisture": final_moisture
            }
            print(message)
                    
            # Convert message to string
            message_str = (f"Initial: {initial_moisture:.2f}%, Duration: {pump_duration:.2f}s, Water Used: {water_used:.2f}L, Final: {final_moisture:.2f}%")
            print(message_str)
                    
            # Encode message as binary data
            # Neccesary for appropriate Chirstack decoding
            payload = struct.pack('@ffff', initial_moisture, pump_duration, water_used, final_moisture)
            print(payload)

            # Send data over LoRa
            lora.send_data(data=payload, data_length=len(payload), frame_counter=frame_counter)
            lora.receive()
                    
            # Incrimenting frame counter
            frame_counter += 1
            # Saving last frame counter for future use even with device shutdown
            save_frame_counter(frame_counter)

        utime.sleep(read_delay)

# Initialising main function to loop indefinitely
if __name__ == "__main__":
    main()
