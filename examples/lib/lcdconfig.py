# /*****************************************************************************
# * | File        :   epdconfig.py
# * | Author      :   Adapted from Waveshare by ChatGPT
# * | Function    :   Hardware interface using lgpio (Python 3.11 compatible)
# ******************************************************************************

import os
import sys
import time
import spidev
import logging
import numpy as np
import lgpio

class RaspberryPi:
    def __init__(self, spi=spidev.SpiDev(0, 0), spi_freq=40000000,
                 rst=27, dc=25, bl=18, bl_freq=1000, i2c=None, i2c_freq=100000):

        self.np = np
        self.RST_PIN = rst
        self.DC_PIN = dc
        self.BL_PIN = bl
        self.SPEED = spi_freq
        self.BL_freq = bl_freq

        # Open GPIO chip
        self.h = lgpio.gpiochip_open(0)

        # Set pins as output
        lgpio.gpio_claim_output(self.h, self.RST_PIN)
        lgpio.gpio_claim_output(self.h, self.DC_PIN)
        lgpio.gpio_claim_output(self.h, self.BL_PIN)

        # Enable backlight
        lgpio.gpio_write(self.h, self.BL_PIN, 1)

        # Initialize SPI
        self.SPI = spi
        if self.SPI is not None:
            self.SPI.max_speed_hz = spi_freq
            self.SPI.mode = 0b00

        # PWM (simulate via software if needed)
        self._bl_duty = 100

    def digital_write(self, pin, value):
        lgpio.gpio_write(self.h, pin, value)

    def digital_read(self, pin):
        return lgpio.gpio_read(self.h, pin)

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        if self.SPI is not None:
            self.SPI.writebytes(data)

    def bl_DutyCycle(self, duty):
        self._bl_duty = duty
        # NOTE: lgpio doesn't support software PWM directly on all pins
        # You can later replace this with pigpio or hardware PWM driver
        # Here we simulate: 0 = off, 1-100 = on
        lgpio.gpio_write(self.h, self.BL_PIN, 1 if duty > 0 else 0)

    def bl_Frequency(self, freq):
        self.BL_freq = freq
        # No effect unless PWM is hardware implemented

    def module_init(self):
        lgpio.gpio_claim_output(self.h, self.RST_PIN)
        lgpio.gpio_claim_output(self.h, self.DC_PIN)
        lgpio.gpio_claim_output(self.h, self.BL_PIN)
        self.bl_DutyCycle(self._bl_duty)

        if self.SPI is not None:
            self.SPI.max_speed_hz = self.SPEED
            self.SPI.mode = 0b00

        return 0

    def module_exit(self):
        logging.debug("spi end")
        if self.SPI is not None:
            self.SPI.close()

        logging.debug("gpio cleanup...")
        lgpio.gpio_write(self.h, self.RST_PIN, 1)
        lgpio.gpio_write(self.h, self.DC_PIN, 0)
        lgpio.gpio_write(self.h, self.BL_PIN, 1)
        lgpio.gpiochip_close(self.h)

### END OF FILE ###
