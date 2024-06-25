# Copyright 2021 LeMaRiva|tech lemariva.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
# ES32 TTGO v1.0 
device_config = {
    'spi_unit': 1,
    'miso':19,
    'mosi':27,
    'ss':18,
    'sck':5,
    'dio_0':26,
    'reset':14,
    'led':2, 
}

# SparkFun WRL-15006 ESP32 LoRa Gateway
device_config = {
    'spi_unit': 1,
    'miso':12,
    'mosi':13,
    'ss':16,
    'sck':14,
    'dio_0':26,
    'reset':36,
    'led':17, 
}
# M5Stack ATOM Matrix
device_config = {
    'spi_unit': 1,
    'miso':23,
    'mosi':19,
    'ss':22,
    'sck':33,
    'dio_0':25,
    'reset':21,
    'led':12, 
}

#M5Stack & LoRA868 Module
device_config = {
    'spi_unit': 1,
    'miso':19,
    'mosi':23,
    'ss':5,
    'sck':18,
    'dio_0':26,
    'reset':36,
    'led':12, 
}

# RASPBERRY PI Pico 
device_config = {
    'spi_unit': 0,
    'miso':4,
    'mosi':3,
    'ss':5,
    'sck':2,
    'dio_0':6,
    'reset':7,
    'led':25, 
}

"""

# Device vconfigurations for raspberry pi pico
device_config = {
    'spi_unit': 0,
    'miso':4,
    'mosi':3,
    'ss':1,
    'sck':2,
    'dio_0':5,
    'reset':0,
    'led':18, 
}

app_config = {
    'loop': 200,
    'sleep': 100,
}

lora_parameters = {
    'tx_power_level': 2, 
    'signal_bandwidth': 'SF7BW125',
    'spreading_factor': 7,    
    'coding_rate': 5, 
    'sync_word': 0x34, 
    'implicit_header': False,
    'preamble_length': 8,
    'enable_CRC': True,
    'invert_IQ': False,
}

wifi_config = {
    'ssid':'',
    'password':''
}

# Device credentials for server access
ttn_config = {
    'devaddr': bytearray([0x26, 0x0B, 0x4A, 0x9E]),
    'nwkey': bytearray([0xB6, 0xDA, 0x0D, 0x4D, 0xF3, 0x7E, 0x4B, 0x80, 0x23, 0x3D, 0x38, 0x45, 0x3F, 0x47, 0x10, 0xC7]),
    'app': bytearray([0x8C, 0x43, 0xA7, 0x83, 0x85, 0x4B, 0xF5, 0xB4, 0x6F, 0xBE, 0x2F, 0xE0, 0x7E, 0x9B, 0xD0, 0xF8]),
    'country': 'EU',
}