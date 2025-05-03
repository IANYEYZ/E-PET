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
import numpy as np
import pyaudio # type: ignore
from queue import Queue
import threading
import time

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
        self.pyaudio_instance = pyaudio.PyAudio()
        self.format = pyaudio.paFloat32 if dtype == 'float32' else pyaudio.paInt16

    def _callback(self, in_data, frame_count, time_info, status):
        """音频流回调函数，将音频数据放入队列"""
        if in_data:
            audio_data = np.frombuffer(in_data, dtype=self.dtype)
            if self.channels > 1:
                audio_data = audio_data.reshape(-1, self.channels)
            self.audio_queue.put(audio_data)
        return (None, pyaudio.paContinue)

    def _record_async(self):
        """异步录制线程函数"""
        self.stream = self.pyaudio_instance.open(
            format=self.format,
            channels=self.channels,
            rate=self.samplerate,
            input=True,
            stream_callback=self._callback,
            frames_per_buffer=1024
        )
        self.stream.start_stream()
        while self.is_recording:
            time.sleep(0.1)  # 防止CPU占用过高
        self.stream.stop_stream()
        self.stream.close()

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

    def recordUntilSilence(self, silence_duration=1.0, initial_noise_duration=1.0):
        """
        录制音频直到检测到指定时长的沉默（阻塞）
        只有在检测到有效语音后才开始判断沉默，使用短时能量和自适应阈值
        
        参数:
            silence_duration: 沉默持续时间（秒，默认1.0）
            initial_noise_duration: 初始背景噪声采样时间（秒，默认1.0）
        
        返回:
            numpy.ndarray: 录制的音频数据
        """
        audio_chunks = []
        silent_samples = 0
        required_silent_samples = int(self.samplerate * silence_duration)
        chunk_size = 1024
        speech_detected = False
        noise_energy_samples = []
        noise_duration_samples = int(self.samplerate * initial_noise_duration)
        energy_threshold = None
        zcr_threshold = 0.1  # 默认零交叉率阈值

        def calculate_energy(audio_data):
            """计算短时能量"""
            return np.sum(audio_data ** 2) / len(audio_data)

        def calculate_zcr(audio_data):
            """计算零交叉率"""
            signs = np.sign(audio_data)
            signs[signs == 0] = -1
            return len(np.where(np.diff(signs))[0]) / len(audio_data)

        def callback(in_data, frame_count, time_info, status):
            nonlocal silent_samples, audio_chunks, speech_detected, noise_energy_samples, energy_threshold
            if in_data:
                audio_data = np.frombuffer(in_data, dtype=self.dtype)
                if self.channels > 1:
                    audio_data = audio_data.reshape(-1, self.channels)[:, 0]  # 使用第一个声道
                audio_chunks.append(audio_data)
                
                # 计算短时能量和零交叉率
                energy = calculate_energy(audio_data)
                zcr = calculate_zcr(audio_data)
                
                # 初始阶段：收集背景噪声统计
                if len(np.concatenate(audio_chunks)) < noise_duration_samples:
                    noise_energy_samples.append(energy)
                    return (None, pyaudio.paContinue)
                
                # 计算自适应阈值（仅在噪声收集完成后执行一次）
                nonlocal energy_threshold
                if noise_energy_samples and energy_threshold is None:
                    # noise_mean = np.mean(noise_energy_samples)
                    # noise_std = np.std(noise_energy_samples)
                    # energy_threshold = noise_mean + 2 * noise_std if noise_std > 0 else noise_mean * 1.5  # 防止std为0
                    energy_threshold = 0.3
                    noise_energy_samples = []  # 清空
                    print(f"Computed energy threshold: {energy_threshold:.6f}")
                
                # 如果阈值仍未设置，使用默认值
                if energy_threshold is None:
                    energy_threshold = 0.01  # 回退阈值
                
                print(f"能量: {energy:.6f}, 零交叉率: {zcr:.6f}, 语音检测: {speech_detected}, 沉默样本: {silent_samples}")

                # 检测是否有有效语音
                if energy > energy_threshold and zcr > zcr_threshold:
                    speech_detected = True
                    silent_samples = 0
                elif speech_detected:
                    # 只有在检测到语音后才开始累积沉默样本
                    silent_samples += frame_count
                
                # 如果检测到语音且沉默时间超过要求，停止录制
                if speech_detected and silent_samples >= required_silent_samples:
                    return (None, pyaudio.paComplete)
            return (None, pyaudio.paContinue)
        
        os.system('amixer -c 0 cset numid=3 7 > /dev/null 2>&1')

        stream = self.pyaudio_instance.open(
            format=self.format,
            channels=self.channels,
            rate=self.samplerate,
            input=True,
            stream_callback=callback,
            frames_per_buffer=chunk_size
        )
        
        try:
            stream.start_stream()
            while stream.is_active():
                time.sleep(0.1)
        finally:
            stream.stop_stream()
            stream.close()

        if audio_chunks:
            audio_data = np.concatenate(audio_chunks)
            print(f"录制结束（检测到沉默），共录制 {len(audio_data)/self.samplerate:.2f} 秒音频")
            return audio_data
        else:
            print("没有录制到音频数据")
            return np.array([])

    def __del__(self):
        """析构函数，确保资源被释放"""
        if self.is_recording:
            self.stop()
        self.pyaudio_instance.terminate()
