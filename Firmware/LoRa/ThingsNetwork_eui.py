from machine import SPI, Pin
import time

# Define SPI pins
SPI_ID = 0
SCK_PIN = 2
MOSI_PIN = 3
MISO_PIN = 4
NSS_PIN = 1

# Initialize SPI
spi = SPI(SPI_ID, baudrate=5000000, polarity=0, phase=0, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN), miso=Pin(MISO_PIN))

# Function to send and receive data
def send_receive(data):
    # Start SPI transaction
    cs = Pin(NSS_PIN, Pin.OUT)
    cs.value(0)

    # Send data and receive response
    response = spi.read(len(data))
    # ^ In real use, you would likely send data here instead of just reading it

    # End SPI transaction
    cs.value(1)

    return response

# Main function
def send_receive_run():
    # Test communication by sending and receiving data
    data_to_send = b"Hello"
    response = send_receive(data_to_send)
    print("Response:", response)
    
send_receive_run()

# Function to read EUIs
def read_euis():
    # Start SPI transaction
    cs = Pin(NSS_PIN, Pin.OUT)
    cs.value(0)

    # Send command to read EUIs
    spi.write(bytearray([0x01]))  # Read command for RFM69HCW

    # Read JoinEUI (MSB first)
    join_eui = spi.read(8)
    join_eui = int.from_bytes(join_eui, "big")

    # Read DevEUI (MSB first)
    dev_eui = spi.read(8)
    dev_eui = int.from_bytes(dev_eui, "big")

    # End SPI transaction
    cs.value(1)

    return join_eui, dev_eui

# Main function
def read_euis_run():
    join_eui, dev_eui = read_euis()
    print("JoinEUI:", hex(join_eui))
    print("DevEUI:", hex(dev_eui))
    
read_euis_run()

#if __name__ == "__main__":
#    main()
