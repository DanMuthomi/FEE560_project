# Copyright 2015, 2016 Ideetron B.V.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# Modified by Brent Rubell for Adafruit Industries.
# Modified by Alan Peaty for MicroPython port.

#JSON string code to work with lora_test4.py

import machine
import utime
import urandom
import ubinascii
import ulora_encryption
import ujson  # Import ujson for handling JSON strings

# SX1276 operating mode settings
_MODE_SLEEP = const(0x00)
_MODE_STDBY = const(0x01)
_MODE_FSTX = const(0x02)
_MODE_TX = const(0x03)
_MODE_FSRX = const(0x04)
_MODE_RX = const(0x05)
_MODE_ACCESS_SHARED_REG = const(0x40)
_MODE_LORA = const(0x80)
# SX1276 registers
_REG_FIFO = const(0x00)
_REG_OPERATING_MODE = const(0x01)
_REG_FRF_MSB = const(0x06)
_REG_FRF_MID = const(0x07)
_REG_FRF_LSB = const(0x08)
_REG_PA_CONFIG = const(0x09)
_REG_FIFO_POINTER = const(0x0D)
_REG_RSSI_CONFIG = const(0x0E)
_REG_RSSI_COLLISION = const(0x0F)
_REG_FEI_MSB = const(0x1D)
_REG_FEI_LSB = const(0x1E)
_REG_PREAMBLE_DETECT = const(0x1F)
_REG_PREAMBLE_MSB = const(0x20)
_REG_PREAMBLE_LSB = const(0x21)
_REG_PAYLOAD_LENGTH = const(0x22)
_REG_MODEM_CONFIG = const(0x26)
_REG_TIMER1_COEF = const(0x39)
_REG_NODE_ADDR = const(0x33)
_REG_IMAGE_CAL = const(0x3B)
_REG_TEMP_VALUE = const(0x3C)
_REG_DIO_MAPPING_1 = const(0x40)
_REG_VERSION = const(0x42)
_REG_FIFO_BASE_ADDR = const(0x80)

class TTN:
    """ TTN Class.
    """
    def __init__(self, dev_address, net_key, app_key, country="EU"):
        """ Interface for The Things Network.
        """
        self.dev_addr = dev_address
        self.net_key = net_key
        self.app_key = app_key
        self.region = country

    @property
    def device_address(self):
        """ Returns the TTN Device Address.
        """
        return self.dev_addr
    
    @property
    def network_key(self):
        """ Returns the TTN Network Key.
        """
        return self.net_key

    @property
    def application_key(self):
        """ Returns the TTN Application Key.
        """
        return self.app_key
    
    @property
    def country(self):
        """ Returns the TTN Frequency Country.
        """
        return self.region


class uLoRa:
    """ uLoRa Interface.
    """
    # Fixed data rates for SX1276 LoRa
    _DATA_RATES = {
        "SF7BW125":(0x74, 0x72, 0x04), "SF7BW250":(0x74, 0x82, 0x04),
        "SF8BW125":(0x84, 0x72, 0x04), "SF9BW125":(0x94, 0x72, 0x04),
        "SF10BW125":(0xA4, 0x72, 0x04), "SF11BW125":(0xB4, 0x72, 0x0C),
        "SF12BW125":(0xC4, 0x72, 0x0C)
    }
    # SPI write buffer
    _BUFFER = bytearray(2)

    def __init__(self, cs, sck, mosi, miso, irq, rst, ttn_config, datarate="SF7BW125", fport=1, channel=None):
        """ Interface for a Semtech SX1276 module. Sets module up for sending to
        The Things Network.
        """
        self._irq = machine.Pin(irq, machine.Pin.IN)
        self._cs = machine.Pin(cs, machine.Pin.OUT, value=1)
        self._rst = machine.Pin(rst, machine.Pin.OUT, value=1)
        # Set up SPI device on Mode 0
        self._device = machine.SPI(
            id=0,
            baudrate=4000000,
            polarity=0,
            phase=0,
            sck=machine.Pin(sck),
            mosi=machine.Pin(mosi),
            miso=machine.Pin(miso)
        )
        # Verify the version of the SX1276 module
        self._version = self._read_u8(_REG_VERSION)
        if self._version != 18:
            raise TypeError("Can not detect LoRa Module. Please check wiring!")
        # Set Frequency registers
        self._rfm_msb = None
        self._rfm_mid = None
        self._rfm_lsb = None
        # Set datarate registers
        self._sf = None
        self._bw = None
        self._modemcfg = None
        self.set_datarate(datarate)
        self._fport = fport
        # Set regional frequency plan
        if "US" in ttn_config.country:
            from ttn_usa import TTN_FREQS
            self._frequencies = TTN_FREQS
        elif ttn_config.country == "AS":
            from ttn_as import TTN_FREQS
            self._frequencies = TTN_FREQS
        elif ttn_config.country == "AU":
            from ttn_au import TTN_FREQS
            self._frequencies = TTN_FREQS
        elif ttn_config.country == "EU":
            from ttn_eu import TTN_FREQS
            self._frequencies = TTN_FREQS
        else:
            raise TypeError("Country Code Incorrect/Unsupported")
        # Set SX1276 channel number
        self._channel = channel
        self._tx_random = urandom.getrandbits(3)
        if self._channel is not None:
            # Set single channel
            self.set_channel(self._channel)
        # Init FrameCounter
        self.frame_counter = 0
        # Set up SX1276 for LoRa Mode
        for pair in ((_REG_OPERATING_MODE, _MODE_SLEEP), (_REG_OPERATING_MODE, _MODE_LORA),
                     (_REG_PA_CONFIG, 0xFF), (_REG_PREAMBLE_DETECT, 0x25),
                     (_REG_PREAMBLE_MSB, 0x00), (_REG_PREAMBLE_LSB, 0x08),
                     (_REG_MODEM_CONFIG, 0x0C), (_REG_TIMER1_COEF, 0x34),
                     (_REG_NODE_ADDR, 0x27), (_REG_IMAGE_CAL, 0x1D),
                     (_REG_RSSI_CONFIG, 0x80), (_REG_RSSI_COLLISION, 0x00)):
            self._write_u8(pair[0], pair[1])
        # Give the uLoRa object ttn configuration
        self._ttn_config = ttn_config

    def send_data_enc(self, data, data_length, frame_counter, timeout=2):
        """ Function to assemble and send data.
        """
        # Data packet
        enc_data = bytearray(data_length)
        lora_pkt = bytearray(64)
        # Copy bytearray into bytearray for encryption
        enc_data[0:data_length] = data[0:data_length]
        # Encrypt data (enc_data is overwritten in this function)
        self.frame_counter = frame_counter
        aes = ulora_encryption.AES(
            self._ttn_config.device_address,
            self._ttn_config.app_key,
            self._ttn_config.network_key,
            self.frame_counter
        )
        enc_data = aes.encrypt(enc_data)
        # Construct MAC Layer packet (PHYPayload)
        # MHDR (MAC Header) - 1 byte
        lora_pkt[0] = 0x40  # MType: unconfirmed data up, RFU / Major zeroed
        # MACPayload
        # FHDR (Frame Header): DevAddr (4 bytes) - short device address
        lora_pkt[1] = self._ttn_config.device_address[3]
        lora_pkt[2] = self._ttn_config.device_address[2]
        lora_pkt[3] = self._ttn_config.device_address[1]
        lora_pkt[4] = self._ttn_config.device_address[0]
        # FCtrl (Frame Control)
        lora_pkt[5] = 0x00
        # FCnt (Frame Counter)
        lora_pkt[6] = frame_counter & 0x00FF
        lora_pkt[7] = (frame_counter >> 8) & 0x00FF
        # FPort (Frame port)
        lora_pkt[8] = self._fport
        # Copy encrypted data into packet
        for i in range(0, len(enc_data)):
            lora_pkt[9+i] = enc_data[i]
        # Calculate MIC
        mic = aes.calculate_mic(lora_pkt, 9 + len(enc_data))
        # Copy MIC to end of packet
        for i in range(0, len(mic)):
            lora_pkt[9 + len(enc_data) + i] = mic[i]
        # Send data packet
        if self.send_packet(lora_pkt, 9 + len(enc_data) + len(mic), timeout) is False:
            return False
        return True

    def send_packet(self, lora_packet, lora_pkt_length, timeout):
        """ Function to send a LoRa packet.
        """
        # Set operating mode to Standby
        self._write_u8(_REG_OPERATING_MODE, _MODE_STDBY)
        # Set frame length
        self._write_u8(_REG_PAYLOAD_LENGTH, lora_pkt_length)
        # Set base address for TX/RX FIFO
        self._write_u8(_REG_FIFO_POINTER, 0x00)
        # Write packet to FIFO
        for i in range(lora_pkt_length):
            self._write_u8(_REG_FIFO, lora_packet[i])
        # Set operating mode to TX
        self._write_u8(_REG_OPERATING_MODE, _MODE_TX)
        utime.sleep(timeout)
        # Check if packet has been sent
        if self._read_u8(_REG_OPERATING_MODE) != _MODE_TX:
            return False
        return True

    def _write_u8(self, address, data):
        """ Writes byte to address via SPI
        """
        self._cs(0)
        self._BUFFER[0] = (address | 0x80) & 0xFF
        self._BUFFER[1] = data
        self._device.write(self._BUFFER)
        self._cs(1)

    def _read_u8(self, address):
        """ Reads byte from address via SPI
        """
        self._cs(0)
        self._BUFFER[0] = (address & 0x7F) & 0xFF
        self._device.write(self._BUFFER)
        self._device.readinto(self._BUFFER, 2)
        self._cs(1)
        return self._BUFFER[1]

    def set_channel(self, channel):
        """ Sets the channel for the SX1276 Module
        """
        self._rfm_msb = self._frequencies[channel][0]
        self._rfm_mid = self._frequencies[channel][1]
        self._rfm_lsb = self._frequencies[channel][2]
        self._write_u8(_REG_FRF_MSB, self._rfm_msb)
        self._write_u8(_REG_FRF_MID, self._rfm_mid)
        self._write_u8(_REG_FRF_LSB, self._rfm_lsb)

    def set_datarate(self, datarate):
        """ Sets the datarate for the SX1276 Module
        """
        try:
            self._sf = self._DATA_RATES[datarate][0]
            self._bw = self._DATA_RATES[datarate][1]
            self._modemcfg = self._DATA_RATES[datarate][2]
        except KeyError:
            raise TypeError("Invalid Data Rate!")
        self._write_u8(_REG_OPERATING_MODE, _MODE_SLEEP)
        self._write_u8(_REG_OPERATING_MODE, _MODE_LORA)
        self._write_u8(_REG_OPERATING_MODE, _MODE_STDBY)
        self._write_u8(_REG_MODEM_CONFIG, self._modemcfg)
        self._write_u8(_REG_MODEM_CONFIG + 1, self._bw)
        self._write_u8(_REG_MODEM_CONFIG + 2, self._sf)
        self._write_u8(_REG_PAYLOAD_LENGTH, 0x80)
        self._write_u8(_REG_FIFO_BASE_ADDR, 0x80)

    def send_json(self, json_data, frame_counter, timeout=2):
        """ Function to send JSON data.
        """
        # Convert JSON data to string and then to bytes
        json_bytes = ujson.dumps(json_data).encode('utf-8')
        data_length = len(json_bytes)

        # Encrypt and send the data
        return self.send_data_enc(json_bytes, data_length, frame_counter, timeout)
