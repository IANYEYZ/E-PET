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

import sounddevice as sd # type: ignore  
import numpy as np
import noisereduce as nr # type: ignore

class MIC:
    def __init__(self, samplerate=16000, channels=1, dtype='float32'):
        self.samplerate = samplerate
        self.channels = channels
        self.dtype = dtype
        self.recording = False
        self.data = []
        self.stream = None

    def start(self):
        assert not self.recording, "已经在录音"
        self.data = []
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            dtype=self.dtype,
            callback=self.callback
        )
        self.stream.start()
        self.recording = True

    def callback(self, indata, frames, time, status):
        self.data.append(indata.copy())

    def stop(self):
        assert self.recording, "未在录音"
        self.stream.stop()
        self.stream.close()
        self.recording = False
        recorded_data = np.concatenate(self.data, axis=0)
        # reduced_data = nr.reduce_noise(y=recorded_data, sr=self.samplerate)
        reduced_data = recorded_data
        reduced_data = np.array(reduced_data, dtype=self.dtype)
        return reduced_data
