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

from helpers.servo import SERVO

class ARM(SERVO):
    _STOP = 0
    _FORWARD = 1
    _BACKWARD = 2

    _PIN_LEFT = 14
    _PIN_RIGHT = 15

    _SPEED = {
        _PIN_LEFT: {
            _STOP: 0.2,
            _FORWARD: 0.3,
            _BACKWARD: 0.1,
        },
        _PIN_RIGHT: {
            _STOP: 0.2,
            _FORWARD: 0.3,
            _BACKWARD: 0.1,
        },
    }

    def __init__(self):
        super().__init__()

    def left_clockwise(self):
        self._set_servo(self._PIN_LEFT, self._SPEED[self._PIN_LEFT][self._FORWARD])

    def left_counter_clockwise(self):
        self._set_servo(self._PIN_LEFT, self._SPEED[self._PIN_LEFT][self._BACKWARD])

    def left_stop(self):
        self._set_servo(self._PIN_LEFT, self._SPEED[self._PIN_LEFT][self._STOP])

    def right_clockwise(self):
        self._set_servo(self._PIN_RIGHT, self._SPEED[self._PIN_RIGHT][self._FORWARD])

    def right_counter_clockwise(self):
        self._set_servo(self._PIN_RIGHT, self._SPEED[self._PIN_RIGHT][self._BACKWARD])

    def right_stop(self):
        self._set_servo(self._PIN_RIGHT, self._SPEED[self._PIN_RIGHT][self._STOP])
