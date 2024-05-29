from machine import ADC, Pin
import utime
import time
from ulora1 import LoRa, ModemConfig, SPIConfig

# Define LoRa module pins and parameters
RFM95_RST = 0
RFM95_SPIBUS = SPIConfig.rp2_my
RFM95_CS = 1
RFM95_INT = 5
RF95_FREQ = 868.0
RF95_POW = 20
CLIENT_ADDRESS = 1
SERVER_ADDRESS = 2

# Initialize LoRa module
lora = LoRa(RFM95_SPIBUS, RFM95_INT, CLIENT_ADDRESS, RFM95_CS, reset_pin=RFM95_RST, freq=RF95_FREQ, tx_power=RF95_POW, acks=True)

# Define soil moisture sensor and water pump pins
soil = ADC(Pin(26))  # Connect Soil moisture sensor data to Raspberry Pi Pico GP26
pump = Pin(15, Pin.OUT)  # Connect relay control pin for the water pump to GP14

# Calibration values
min_moisture = 0
max_moisture = 65535
pump_on_threshold = 20.0
pump_off_threshold = 50.0

read_delay = 1  # Time between readings

# Pump flow rate in liters per minute (L/min)
pump_flow_rate = 2.0

def read_moisture():
    moisture_adc = soil.read_u16()
    moisture = (max_moisture - moisture_adc) * 100 / (max_moisture - min_moisture)
    return moisture, moisture_adc

while True:
    moisture, moisture_adc = read_moisture()
    print(f"moisture: {moisture:.2f}% (adc: {moisture_adc})")
    
    if moisture < pump_on_threshold:
        initial_moisture = moisture
        pump.value(1)  # Turn on the pump
        start_time = time.time()
        print("Pump turned on.")
        
        while True:
            moisture, moisture_adc = read_moisture()
            print(f"moisture: {moisture:.2f}% (adc: {moisture_adc})")
            
            if moisture >= pump_off_threshold:
                pump.value(0)  # Turn off the pump
                pump_duration = time.time() - start_time  # Duration in seconds
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
                
                # Send data to TTN via LoRa
                lora.send_to_wait(message_str, SERVER_ADDRESS)
                print("Data sent to TTN:", message_str)
                break  # Exit inner while loop
            
            utime.sleep(read_delay)  # Set a delay between readings
            
    utime.sleep(read_delay)  # Set a delay between readings
