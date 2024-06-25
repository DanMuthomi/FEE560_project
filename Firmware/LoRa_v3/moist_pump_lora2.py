import utime
import time
from machine import ADC, Pin
import ujson
from ulora import TTN, uLoRa

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

# LoRa configuration
LORA_CS = const(1)
LORA_SCK = const(2)
LORA_MOSI = const(3)
LORA_MISO = const(4)
LORA_IRQ = const(5)
LORA_RST = const(0)
LORA_DATARATE = "SF9BW125"
LORA_FPORT = const(1)

TTN_DEVADDR = bytearray([0x26, 0x0B, 0x4A, 0x9E])
TTN_NWKEY = bytearray([0xB6, 0xDA, 0x0D, 0x4D, 0xF3, 0x7E, 0x4B, 0x80, 0x23, 0x3D, 0x38, 0x45, 0x3F, 0x47, 0x10, 0xC7])
TTN_APP = bytearray([0x8C, 0x43, 0xA7, 0x83, 0x85, 0x4B, 0xF5, 0xB4, 0x6F, 0xBE, 0x2F, 0xE0, 0x7E, 0x9B, 0xD0, 0xF8])
TTN_CONFIG = TTN(TTN_DEVADDR, TTN_NWKEY, TTN_APP, country="EU")

def read_moisture():
    moisture_adc = soil.read_u16()
    moisture = (max_moisture - moisture_adc) * 100 / (max_moisture - min_moisture)
    return moisture, moisture_adc

def main():
    lora = uLoRa(
        cs=LORA_CS,
        sck=LORA_SCK,
        mosi=LORA_MOSI,
        miso=LORA_MISO,
        irq=LORA_IRQ,
        rst=LORA_RST,
        ttn_config=TTN_CONFIG,
        datarate=LORA_DATARATE,
        fport=LORA_FPORT
    )

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
                    
                    json_data = ujson.dumps(message_str)
                    data = json_data.encode()

                    # Send data over LoRa
                    lora.send_data(data, len(data), lora.frame_counter)
                    lora.frame_counter += 1
                    break
                utime.sleep(read_delay)
                
            utime.sleep(read_delay)

if __name__ == "__main__":
    main()
