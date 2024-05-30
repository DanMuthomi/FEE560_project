# Sample application using the HelTec Automation Wireless Stick development board.
# https://github.com/Heltec-Aaron-Lee/WiFi_Kit_series/blob/master/PinoutDiagram/Wireless_Stick.pdf
# Application takes temperature, pressure and humidity sensor readings using an external BME280,
# and sends them to The Things Network (TTN) using LoRaWAN. Onboard SSD1306 OLED screen and LED
# are used to show useful information.

import utime
from machine import I2C, Pin, deepsleep
import ubinascii
import ujson
#import bme280_float as bme280
#import ssd1306
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
# TTN device address, 4 Bytes, MSB (REPLACE WITH YOUR OWN!!!)
TTN_DEVADDR = bytearray([0x26, 0x0B, 0x4A, 0x9B])
# TTN network session key, 16 Bytes, MSB (REPLACE WITH YOUR OWN!!!)
TTN_NWKEY = bytearray([0xB6, 0xDA, 0x0D, 0x4D, 0xF3, 0x7E, 0x4B, 0x80, 0x23, 0x3D, 0x38, 0x45, 0x3F, 0x47, 0x10, 0xC7])
# TTN application session key, 16 Bytes, MSB (REPLACE WITH YOUR OWN!!!)
TTN_APP = bytearray([0x8C, 0x43, 0xA7, 0x83, 0x85, 0x4B, 0xF5, 0xB4, 0x6F, 0xBE, 0x2F, 0xE0, 0x7E, 0x9B, 0xD0, 0xF8])
TTN_CONFIG = TTN(TTN_DEVADDR, TTN_NWKEY, TTN_APP, country="EU")

# Additional configurations
PROGRAM_LOOP_MS = const(600000)
PROGRAM_WAIT_MS = const(3000)
"""# BME280 temperature, pressure and humidity sensor
BME280_SCL = const(13)
BME280_SDA = const(12)
BME280_FREQ = const(400000)
# Onboard OLED screen
SSD1306_SCL = const(15)
SSD1306_SDA = const(4)
SSD1306_FREQ = const(400000)
SSD1306_SCL_RST = const(16)"""
# Onboard LED
LED_PIN = const(25)

def main():
    start_time = utime.ticks_ms()
    # Turn LED for the duration of the program
    led = Pin(LED_PIN, Pin.OUT, value=1)
    """# Show some information on the onboard OLED
    reset = Pin(SSD1306_SCL_RST, Pin.OUT, value=1)
    i2c_oled = I2C(
        scl=Pin(SSD1306_SCL, Pin.IN, Pin.PULL_UP),
        sda=Pin(SSD1306_SDA, Pin.IN, Pin.PULL_UP),
        freq=SSD1306_FREQ
    )
    oled = ssd1306.SSD1306_I2C(64, 32, i2c_oled)"""
    """# BME280 temperature, pressure and humidity readings
    data = b""
    try:
        i2c_bme = I2C(scl=Pin(BME280_SCL), sda=Pin(BME280_SDA), freq=BME280_FREQ)
        bme = bme280.BME280(i2c=i2c_bme)
        temperature, pressure, humidity = bme.read_compensated_data()
    except (OSError, ValueError, NameError) as e:
        print(e)
        data += b"\x00\x00\x00"
        oled.text(ubinascii.hexlify(data), 0, 16)
        oled.text("ERROR!", 0, 24)
    else:
        print("Measurements:", temperature, "c", pressure, "Pa", humidity, "%")
        # Manipulate sensor values so that they occupy 1 byte each
        # Note how a +128 offset is used for the temperature (c) reading to
        # maintain 1 byte signed
        TEMP_OFFSET = const(128)
        data += round(temperature + TEMP_OFFSET).to_bytes(1, "big")
        data += round(pressure / 1000).to_bytes(1, "big")
        data += round(humidity).to_bytes(1, "big")"""
    data = b"This is a test"  # Convert string to bytes
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
    # Send raw data without any LoRaWAN packet structure
    lora.send_data_raw(b'This is a test')
    print("Sending packet...", lora.frame_counter, ubinascii.hexlify(data))
    lora.send_data(data, len(data), lora.frame_counter)
    print(len(data), "bytes sent!")
    lora.frame_counter += 1
    #oled.text(ubinascii.hexlify(data), 0, 16)
    #oled.text("SENT!", 0, 24)
    """finally:
        oled.show()
        utime.sleep_ms(PROGRAM_WAIT_MS)
        led.off()
        deepsleep(PROGRAM_LOOP_MS - (utime.ticks_ms() - start_time))"""

if __name__ == "__main__":
    main()
