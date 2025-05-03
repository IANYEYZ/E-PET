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

import os
import sounddevice as sd # type: ignore
from threading import Thread
import pyaudio # type: ignore
import numpy as np
import alsaaudio # type: ignore

class SPEAKER:
    def __init__(self):
        dev = next((d for d in sd.query_devices() if d['max_output_channels'] > 0 and 'usb' in d['name'].lower()), None)
        if dev: os.environ['ALSA_CARD'] = str(dev['index'])
        # 设置音量
        m = alsaaudio.Mixer('Master')
        # 设置音量为最大 100%
        m.setvolume(100)
        self.playing = False

    def play(self, file):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=44100,
                            output=True)
        wav_bytes = open("media/" + file, "rb").read()
        audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
        stream.write(audio_np.tobytes())
        
    def speechOn(self):
        self.play("Speech On.wav")

    def speechOff(self):
        self.play("Speech Off.wav")

    def _balloonDo(self):
        while self.playingThreadPlay:
            self.play("ding.wav")

    def balloonStart(self):
        self.playingThreadPlay = True
        self.playingThread = Thread(target=self._balloonDo)

    def balloonStop(self):
        self.playingThreadPlay = False
