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

class WHEEL(SERVO):
    _STOP = 0
    _FORWARD = 1
    _BACKWARD = 2

    _PIN_FRONT_LEFT = 0
    _PIN_FRONT_RIGHT = 1
    _PIN_BACK_LEFT = 2
    _PIN_BACK_RIGHT = 3

    _SPEED = {
        _PIN_FRONT_LEFT: {
            _STOP: 0.2,
            _FORWARD: 1,
            _BACKWARD: -0.3,
        },
        _PIN_FRONT_RIGHT: {
            _STOP: 0.2,
            _FORWARD: 0.4,
            _BACKWARD: -1,
        },
        _PIN_BACK_LEFT: {
            _STOP: 0.2,
            _FORWARD: 1,
            _BACKWARD: -0.3,
        },
        _PIN_BACK_RIGHT: {
            _STOP: 0.2,
            _FORWARD: 0.4,
            _BACKWARD: -1,
        },
    }

    def __init__(self):
        super().__init__()

    def _set_all_servo(self, mode):
        self._set_servo(self._PIN_FRONT_LEFT, self._SPEED[self._PIN_FRONT_LEFT][mode[0]])
        self._set_servo(self._PIN_FRONT_RIGHT, self._SPEED[self._PIN_FRONT_RIGHT][mode[1]])
        self._set_servo(self._PIN_BACK_LEFT, self._SPEED[self._PIN_BACK_LEFT][mode[2]])
        self._set_servo(self._PIN_BACK_RIGHT, self._SPEED[self._PIN_BACK_RIGHT][mode[3]])

    def straight(self):
        self._set_all_servo([self._FORWARD, self._BACKWARD, self._FORWARD, self._BACKWARD])

    def right(self):
        self._set_all_servo([self._FORWARD, self._FORWARD, self._BACKWARD, self._BACKWARD])

    def left(self):
        self._set_all_servo([self._BACKWARD, self._BACKWARD, self._FORWARD, self._FORWARD])

    def rotate_clockwise(self):
        self._set_all_servo([self._FORWARD, self._FORWARD, self._FORWARD, self._FORWARD])

    def rotate_counterclockwise(self):
        self._set_all_servo([self._BACKWARD, self._BACKWARD, self._BACKWARD, self._BACKWARD])

    def back(self):
        self._set_all_servo([self._BACKWARD, self._FORWARD, self._BACKWARD, self._FORWARD])

    def stop(self):
        self._set_all_servo([self._STOP, self._STOP, self._STOP, self._STOP])
