from machine import SPI, Pin
import time
import struct
from network import LoRa

# Define SPI pins
SPI_ID = 0
SCK_PIN = 2
MOSI_PIN = 3
MISO_PIN = 4
NSS_PIN = 1

# TTN parameters
dev_eui = bytearray.fromhex('5695130620360003000')  # Device EUI
app_eui = bytearray.fromhex('0000000000000000')  # Application EUI
app_key = bytearray.fromhex('88A05B55578DEEAC481105C99A6AFA36')  # Application Key
band = LoRa.EU868
channels = (0, 1, 2)  # EU868 channels

# Initialize SPI
spi = SPI(SPI_ID, baudrate=5000000, polarity=0, phase=0, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN), miso=Pin(MISO_PIN))

# Function to send LoRaWAN data to TTN
def send_lorawan_data(data):
    # Initialize LoRaWAN
    lora = LoRa(mode=LoRa.LORAWAN, region=band, frequency=867500000)
    lora.init(mode=LoRa.LORAWAN, adr=False, public=False, tx_iq=True, channels=channels)

    # Join network
    lora.join(activation=LoRa.ABP, auth=(dev_eui, app_eui, app_key))

    # Wait for the join to complete
    while not lora.has_joined():
        time.sleep(2.5)

    # Send data
    lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    lora_sock.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)  # Set data rate
    lora_sock.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, False)  # Set unconfirmed data uplink
    lora_sock.send(data)

# Main function
def main():
    # Send LoRaWAN data to TTN
    dummy_data = struct.pack(">H", 1234)  # Pack an integer (1234) into a 2-byte string
    send_lorawan_data(dummy_data)

if __name__ == "__main__":
    main()
