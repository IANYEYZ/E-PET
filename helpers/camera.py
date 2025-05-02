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

import base64
import cv2 # type: ignore
from PIL import Image

class CAMERA:
    def shot(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return None
        else:
            for _ in range(5):
                cap.read()
            ret, frame = cap.read()
            cap.release()
            if ret:
                _, buffer = cv2.imencode('.png', frame)
                return base64.b64encode(
                    buffer
                ).decode('utf-8')
            else:
                return None

camera = CAMERA()
