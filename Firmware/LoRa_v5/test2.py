import utime
import struct
import urandom
import ujson
from sx127x import TTN, SX127x
from machine import Pin, SPI, ADC
from config import *

# Define soil moisture sensor and water pump pins
soil = ADC(Pin(26))  # Connect Soil moisture sensor data to Raspberry Pi Pico GP26S
pump = Pin(15, Pin.OUT)  # Connect relay control pin for the water pump to GP14

# Calibration values
min_moisture = 0
max_moisture = 65535
pump_on_threshold = 20.0
pump_off_threshold = 50.0

read_delay = 5  # Time between readings

# Pump flow rate in liters per minute (L/min)
pump_flow_rate = 2.0

__DEBUG__ = True
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

ttn_config = TTN(ttn_config['devaddr'], ttn_config['nwkey'], ttn_config['app'], country=ttn_config['country'])

device_spi = SPI(device_config['spi_unit'], baudrate = 10000000, 
        polarity = 0, phase = 0, bits = 8, firstbit = SPI.MSB,
        sck = Pin(device_config['sck'], Pin.OUT, Pin.PULL_DOWN),
        mosi = Pin(device_config['mosi'], Pin.OUT, Pin.PULL_UP),
        miso = Pin(device_config['miso'], Pin.IN, Pin.PULL_UP))

lora = SX127x(device_spi, pins=device_config, lora_parameters=lora_parameters, ttn_config=ttn_config)
frame_counter = load_frame_counter()

def on_receive(lora, outgoing):
    payload = lora.read_payload()
    print(payload)

lora.on_receive(on_receive)
lora.receive()

def read_moisture():
    moisture_adc = soil.read_u16()
    moisture = (max_moisture - moisture_adc) * 100 / (max_moisture - min_moisture)
    return moisture, moisture_adc

def main():
    frame_counter = load_frame_counter()
    while True:
        moisture, moisture_adc = read_moisture()
        print(f"moisture: {moisture:.2f}% (adc: {moisture_adc})")
        
        if moisture < pump_on_threshold:
            initial_moisture = moisture
            pump.value(1)  # Turn on the pump
            start_time = utime.time()
            print("Pump turned on.")
            
            while True:
                moisture, moisture_adc = read_moisture()
                print(f"moisture: {moisture:.2f}% (adc: {moisture_adc})")
                
                if moisture >= pump_off_threshold:
                    pump.value(0)  # Turn off the pump
                    pump_duration = utime.time() - start_time  # Duration in seconds
                    final_moisture = moisture
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
                    
                    #json_data = ujson.dumps(message_str)
                    #print(json_data)
                    message2 = ujson.dumps(message, separators=(',', ':'))
                    print(message2)
                    escaped_message = message2.replace('"', '\\22')
                    print(escaped_message)
                    jdata = escaped_message.encode()
                    print(jdata)

                    # Send data over LoRa
                    lora.send_data(data=jdata, data_length=len(jdata), frame_counter=frame_counter)
                    lora.receive()
                    
                    frame_counter += 1
                    save_frame_counter(frame_counter)
                    break
                utime.sleep(read_delay)
                
            utime.sleep(read_delay)

if __name__ == "__main__":
    main()
