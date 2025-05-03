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

# 初始化代码，仅需执行一次

# 📦 导入库
import os
import sounddevice as sd # type: ignore
import simpleaudio as sa # type: ignore
from threading import Thread

class SPEAKER:
    def __init__(self):
        dev = next((d for d in sd.query_devices() if d['max_output_channels'] > 0 and 'usb' in d['name'].lower()), None)
        if dev: os.environ['ALSA_CARD'] = str(dev['index'])
        self.playing = False

    def play(self, file):
        self.playing = True
        self.wave_obj = sa.WaveObject.from_wave_file(file)
        self.play_obj = self.wave_obj.play()
        
    def stop(self):
        if self.playing:
            self.play_obj.stop()
            self.playing = False
        elif self.playingThread:
            self.playingThreadPlay = False
            self.playingThread.join()
            self.playing = False
        else:
            print("No sound is playing.")

    def speechOn(self):
        self.play("media/Speech On.wav")

    def speechOff(self):
        self.play("media/Speech Off.wav")

    def _balloonDo(self):
        while self.playingThreadPlay:
            self.play("media/Balloon Forever.wav")
            self.play_obj.wait_done()
            self.playing = False

    def balloonForever(self):
        self.playingThreadPlay = True
        self.playingThread = Thread(target=self._balloonDo)
