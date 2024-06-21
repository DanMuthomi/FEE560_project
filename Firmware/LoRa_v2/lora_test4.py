#JSON string code to work with ulora_4.py
import utime
import ujson  # Import ujson for JSON handling
from machine import Pin
from ulora import TTN, uLoRa

# Heltec ESP32 LoRa V2 development board SPI pins
LORA_CS = const(1)
LORA_SCK = const(2)
LORA_MOSI = const(3)
LORA_MISO = const(4)
LORA_IRQ = const(5)
LORA_RST = const(0)
LORA_DATARATE = "SF9BW125"
LORA_FPORT = const(1)

# The Things Network (TTN) device details (available in TTN console)
TTN_DEVADDR = bytearray([0x26, 0x0B, 0x4A, 0x9B])
TTN_NWKEY = bytearray([0xB6, 0xDA, 0x0D, 0x4D, 0xF3, 0x7E, 0x4B, 0x80, 0x23, 0x3D, 0x38, 0x45, 0x3F, 0x47, 0x10, 0xC7])
TTN_APP = bytearray([0x8C, 0x43, 0xA7, 0x83, 0x85, 0x4B, 0xF5, 0xB4, 0x6F, 0xBE, 0x2F, 0xE0, 0x7E, 0x9B, 0xD0, 0xF8])
TTN_CONFIG = TTN(TTN_DEVADDR, TTN_NWKEY, TTN_APP, country="EU")

# Additional configurations
PROGRAM_LOOP_MS = const(600000)
PROGRAM_WAIT_MS = const(3000)

LED_PIN = const(25)

def main():
    start_time = utime.ticks_ms()
    # Turn LED for the duration of the program
    led = Pin(LED_PIN, Pin.OUT, value=1)
    
    # Construct your JSON data
    data = {
        "sensor_id": 1,
        "moisture_level": 78,
        "temperature": 22.5
    }
    
    # LoRaWAN / TTN send
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
    print("Sending packet...", lora.frame_counter, data)
    lora.send_json(data, lora.frame_counter)
    print(len(ujson.dumps(data)), "characters sent!")
    lora.frame_counter += 1

if __name__ == "__main__":
    main()
