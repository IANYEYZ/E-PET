# Copyright (C) 2025 Langning Chen
# 
# This file is part of E-PET.
# 
# E-PET is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# E-PET is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with E-PET.  If not, see <https://www.gnu.org/licenses/>.


import time
from adafruit_servokit import ServoKit # type: ignore

class SERVO:
    _STOP = 0.2
    _FORWARD = 1
    _BACKWARD = -1

    def __init__(self):
        self._kit = ServoKit(channels = 16)

    def _set_servo(self, pin, mode):
        self._kit.continuous_servo[pin].throttle = mode
