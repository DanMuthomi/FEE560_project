#!/usr/bin/env python3
import sys
import argparse
from time import sleep
from SX127x.LoRa import *
from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config_ada import BOARD
import LoRaWAN
from LoRaWAN.MHDR import MHDR
from random import randrange
import reset_ada
# Import the SSD1306 module.
import adafruit_ssd1306
from digitalio import DigitalInOut, Direction, Pull
import board
import busio

import RPi.GPIO as GPIO

import helium
import keys
import frame

TIMEOUT = 50
# Button A
btnA = DigitalInOut(board.D5)
btnA.direction = Direction.INPUT
btnA.pull = Pull.UP

# Button B
btnB = DigitalInOut(board.D6)
btnB.direction = Direction.INPUT
btnB.pull = Pull.UP

# Button C
btnC = DigitalInOut(board.D12)
btnC.direction = Direction.INPUT
btnC.pull = Pull.UP

BOARD.setup()
parser = LoRaArgumentParser("LoRaWAN sender")

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# 128x32 OLED Display
reset_pin = DigitalInOut(board.D4)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)
# Clear the display.
display.fill(0)
display.text('Helium Texter', 7, 7, 1)
display.show()
width = display.width
height = display.height

class LoRaWANotaa(LoRa):
    def __init__(self, verbose = False):
        super(LoRaWANotaa, self).__init__(verbose)
        self.ack = False
        self.msg_index = 0
        self.msgs = ['On my way.','LOL','Yes.','No.','Maybe.','Call me.',':)',':(']
        self.waiting = False
        self.timeout = 0

    def on_rx_done(self):
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        print("Raw payload: {}".format(payload))

        lorawan = LoRaWAN.new(keys.nwskey, keys.appskey)
        lorawan.read(payload)
        decoded = "".join(list(map(chr, lorawan.get_payload())))
        print("Decoded: {}".format(decoded))
        print("\n")
        
        if lorawan.get_mhdr().get_mtype() == MHDR.UNCONF_DATA_DOWN:
            print("Unconfirmed data down.")
            downlink = decoded
            res = lorawan.mac_payload.get_fhdr().get_fctrl()
            if 0x20 & res != 0: # Check Ack bit.
                print("Server ack")
                if len(downlink) == 0:
                    downlink = "Server ack"
        elif lorawan.get_mhdr().get_mtype() == MHDR.CONF_DATA_DOWN:
            print("Confirmed data down.")
            self.ack = True
            downlink = decoded            
        elif lorawan.get_mhdr().get_mtype() == MHDR.CONF_DATA_UP:
            print("Confirmed data up.")
            downlink = decoded                        
        else:
            print("Other packet.")
            downlink = ''

        self.set_mode(MODE.STDBY)

        s = ''
        s += " pkt_snr_value  %f\n" % self.get_pkt_snr_value()
        s += " pkt_rssi_value %d\n" % self.get_pkt_rssi_value()
        s += " rssi_value     %d\n" % self.get_rssi_value()
        s += " msg: %s" % downlink
        print(s)
        self.update("Rx: {}".format(downlink))
        self.waiting = False
        self.timeout = 0

    def increment(self):
        self.tx_counter += 1
        data_file = open("frame.py", "w")
        data_file.write(
            'frame = {}\n'.format(self.tx_counter))        
        data_file.close()

    def tx(self, msg="", conf=False):
        if len(msg) > 0:
            self.update("Sending message...")
        else:
            self.update("Checking for msgs...")        
        if conf:
            data = MHDR.CONF_DATA_UP
            print('Sending confirmed data up.')
        else:
            data = MHDR.UNCONF_DATA_UP
            print('Sending unconfirmed data up.')            
        self.increment()

        lorawan = LoRaWAN.new(keys.nwskey, keys.appskey)
        if self.ack:
            print('Sending with Ack {}'.format(self.tx_counter))
            lorawan.create(data, {'devaddr': keys.devaddr, 'fcnt': self.tx_counter, 'data': list(map(ord, msg)), 'ack':True})
            self.ack = False
        else:
            print('Sending without Ack {}'.format(self.tx_counter))
            lorawan.create(data, {'devaddr': keys.devaddr, 'fcnt': self.tx_counter, 'data': list(map(ord, msg))})
        print("tx: {}".format(lorawan.to_raw()))
        self.write_payload(lorawan.to_raw())
        self.set_mode(MODE.TX)


    def update(self,msg=''):
        display.fill(0)
        display.text('Outgoing msg: {}'.format(self.msgs[self.msg_index]), 0, 0, 1)
        display.text(msg, 0, 12, 1)
        height = 24
        display.text('Change', 0, height, 1)                
        display.text('Send', 50, height, 1)                
        display.text('Get', 96, height, 1)                
        display.show()

    def start(self):
        self.update()
        while True:
            sleep(.1)
            if not btnA.value: # Select message.
                self.msg_index += 1
                if self.msg_index >= len(self.msgs):
                    self.msg_index = 0
                self.update()
            if not btnB.value: # Send message.
                self.setup_tx()
                msg = self.msgs[self.msg_index]
                self.tx(msg)    
                self.timeout = TIMEOUT
            if not btnC.value: # Check for incoming messages.
                self.waiting = True
                self.timeout = TIMEOUT
                self.setup_tx()
                self.tx()   
            if self.timeout > 0:
                self.timeout -= 1
                if self.timeout == 0:
                    if self.waiting:
                        self.update("No msg received.")
                        self.waiting = False   
                    else:
                        self.update()
                     

    def set_frame(self,frame):
        self.tx_counter = frame

    def setup_tx(self):
        self.clear_irq_flags(RxDone=1)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([1,0,0,0,0,0])
        self.set_freq(helium.UPFREQ)
        self.set_bw(7)
        self.set_spreading_factor(7)
        self.set_pa_config(max_power=0x0F, output_power=0x0E)
        self.set_sync_word(0x34)
        self.set_rx_crc(True)
        self.set_invert_iq(0)
        assert(self.get_agc_auto_on() == 1)        

    def on_tx_done(self):
        self.clear_irq_flags(TxDone=1)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0,0,0,0,0,0])
        self.set_freq(helium.DOWNFREQ)         
        self.set_bw(9)
        self.set_spreading_factor(7)        
        self.set_pa_config(pa_select=1)
        self.set_sync_word(0x34)
        self.set_rx_crc(True)
        self.set_invert_iq(1)

        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

def init(frame):
    lora = LoRaWANotaa(False)
    lora.set_frame(frame)

    try:
        print("Sending LoRaWAN tx\n")
        lora.start()
    except KeyboardInterrupt:
        sys.stdout.flush()
        print("\nKeyboardInterrupt")
    finally:
        sys.stdout.flush()
        lora.set_mode(MODE.SLEEP)
        BOARD.teardown()


def main():
    global msg
    msg = 'Test'
    init(frame.frame)

if __name__ == "__main__":
    main()