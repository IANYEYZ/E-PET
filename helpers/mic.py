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
from queue import Queue
import threading

# class MIC:
#     def __init__(self, samplerate=44100, channels=1, dtype='float32'):
#         self.samplerate = samplerate
#         self.channels = channels
#         self.dtype = dtype
#         self.recording = False
#         self.data = []
#         self.stream = None

#     def start(self):
#         assert not self.recording, "已经在录音"
#         self.data = []
#         self.stream = sd.InputStream(
#             samplerate=self.samplerate,
#             channels=self.channels,
#             dtype=self.dtype,
#             callback=self.callback
#         )
#         self.stream.start()
#         self.recording = True

#     def callback(self, indata, frames, time, status):
#         self.data.append(indata.copy())

#     def stop(self):
#         assert self.recording, "未在录音"
#         self.stream.stop()
#         self.stream.close()
#         self.recording = False
#         recorded_data = np.concatenate(self.data, axis=0)
#         # reduced_data = nr.reduce_noise(y=recorded_data, sr=self.samplerate)
#         reduced_data = recorded_data
#         reduced_data = np.array(reduced_data, dtype=self.dtype)
#         return reduced_data

class MIC:
    def __init__(self, samplerate=44100, channels=1, dtype='float32'):
        """
        初始化麦克风录制类
        
        参数:
            samplerate: 采样率 (默认44100Hz)
            channels: 声道数 (默认1)
            dtype: 音频数据类型 (默认'float32')
        """
        self.samplerate = samplerate
        self.channels = channels
        self.dtype = dtype
        self.audio_queue = Queue()
        self.stream = None
        self.recording_thread = None
        self.is_recording = False

    def _callback(self, indata, frames, time, status):
        """音频流回调函数，将音频数据放入队列"""
        if status:
            print(f"音频流状态: {status}")
        self.audio_queue.put(indata.copy())

    def _record_async(self):
        """异步录制线程函数"""
        with sd.InputStream(samplerate=self.samplerate,
                           channels=self.channels,
                           dtype=self.dtype,
                           callback=self._callback):
            while self.is_recording:
                sd.sleep(100)  # 防止CPU占用过高

    def start(self):
        """
        开始非阻塞式录制
        启动后会立即返回，录制在后台进行
        """
        if self.is_recording:
            print("已经在录制中")
            return
        
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self._record_async)
        self.recording_thread.start()
        print("麦克风录制已开始...")

    def stop(self):
        """
        停止录制并返回录制的音频数据
        
        返回:
            numpy.ndarray: 录制的音频数据
        """
        if not self.is_recording:
            print("没有正在进行的录制")
            return np.array([])
        
        self.is_recording = False
        self.recording_thread.join()
        
        # 收集所有音频数据
        audio_chunks = []
        while not self.audio_queue.empty():
            audio_chunks.append(self.audio_queue.get())
        
        if audio_chunks:
            audio_data = np.concatenate(audio_chunks)
            print(f"录制结束，共录制 {len(audio_data)/self.samplerate:.2f} 秒音频")
            return audio_data
        else:
            print("没有录制到音频数据")
            return np.array([])

    def __del__(self):
        """析构函数，确保资源被释放"""
        if self.is_recording:
            self.stop()