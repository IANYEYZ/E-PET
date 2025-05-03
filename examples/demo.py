import os
import time
import threading
import base64
import numpy as np
from PIL import Image
import sounddevice as sd
import simpleaudio as sa
import alsaaudio
import lgpio
import cv2
import dashscope

from scipy.io.wavfile import write
from adafruit_servokit import ServoKit
from lib import LCD_2inch
from dashscope import MultiModalConversation
from openai import OpenAI

# 设置 API 密钥
API_KEY = "sk-da685c1884eb4d1b8b3e5320cc7324d4"
dashscope.api_key = API_KEY
os.environ['DASHSCOPE_API_KEY'] = API_KEY

# 初始化音频设备
dev = next((d for d in sd.query_devices() if d['max_output_channels'] > 0 and 'usb' in d['name'].lower()), None)
if dev:
    os.environ['ALSA_CARD'] = str(dev['index'])

# 设置音量
mixer = alsaaudio.Mixer('PCM')
mixer.setvolume(70)

# 初始化伺服控制
kit = ServoKit(channels=16)
arm_left = kit.continuous_servo[14]
arm_right = kit.continuous_servo[15]
wheel_front_left = kit.continuous_servo[0]
wheel_front_right = kit.continuous_servo[1]
wheel_back_left = kit.continuous_servo[2]
wheel_back_right = kit.continuous_servo[3]

# 初始化电机为停止状态
arm_left.throttle = 0.1
arm_right.throttle = 0.1
wheel_front_left.throttle = 0.1
wheel_front_right.throttle = 0.1
wheel_back_left.throttle = 0.1
wheel_back_right.throttle = 0.1

# 初始化触摸传感器
h = lgpio.gpiochip_open(0)
touch_pin = 17
lgpio.gpio_claim_input(h, touch_pin)

# 初始化显示屏
disp = LCD_2inch.LCD_2inch()
disp.Init()

# 显示启动画面
try:
    show_startup = True
    # 使用 blink.gif 作为启动画面
    gif = Image.open('emotions/blink.gif')
    for i in range(gif.n_frames):
        gif.seek(i)
        image = gif.convert("RGB")
        disp.ShowImage(image)
        time.sleep(0.05)
except Exception as e:
    print(f"显示启动画面时出错: {e}")

# 音频采样率
fs = 44100

# 表情GIF文件
emotions = {
    'happy': 'emotions/happy.gif',
    'sad': 'emotions/sad.gif',
    'blink': 'emotions/blink.gif',
    'dizzy': 'emotions/dizzy.gif',
    'sleep': 'emotions/sleep.gif'
}

# 函数定义
def record_audio(seconds=3, filename="recording.wav"):
    """录制音频"""
    print(f"开始录音，持续 {seconds} 秒")
    # 录制音频
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()  # 等待录音完成
    print("录音结束")
    
    # 将浮点格式转换为整数格式
    myrecording = np.int16(myrecording / np.max(np.abs(myrecording)) * 32767)
    
    # 保存音频文件
    write(filename, fs, myrecording)
    return filename

def play_audio(filename, volume=70):
    """播放音频文件"""
    mixer.setvolume(volume)
    try:
        wave_obj = sa.WaveObject.from_wave_file(filename)
        play_obj = wave_obj.play()
        play_obj.wait_done()
    except Exception as e:
        print(f"播放音频时出错: {e}")

def play_audio_from_array(audio_array, samplerate=24000, volume=70):
    """从数组播放音频"""
    mixer.setvolume(volume)
    try:
        audio_stereo = np.repeat(audio_array.reshape(-1, 1), 2, axis=1)
        sd.play(audio_stereo, samplerate=samplerate)
        sd.wait()
    except Exception as e:
        print(f"播放音频数组时出错: {e}")

def show_emotion(emotion, loops=1):
    """显示情绪动画"""
    if emotion not in emotions:
        print(f"未找到情绪: {emotion}")
        return
    
    try:
        gif_path = emotions[emotion]
        gif = Image.open(gif_path)
        for _ in range(loops):
            for i in range(gif.n_frames):
                gif.seek(i)
                image = gif.convert("RGB")
                disp.ShowImage(image)
                time.sleep(0.05)
    except Exception as e:
        print(f"显示情绪动画时出错: {e}")

def move_arms(left_speed=0.2, right_speed=0.2, duration=0.5):
    """移动手臂"""
    arm_left.throttle = left_speed
    arm_right.throttle = right_speed
    time.sleep(duration)
    arm_left.throttle = 0.1
    arm_right.throttle = 0.1

def move_wheels(forward=True, speed=0.3, duration=1.0):
    """移动轮子"""
    if forward:
        wheel_front_left.throttle = 0.1 - speed
        wheel_front_right.throttle = 0.1 + speed
        wheel_back_left.throttle = 0.1 - speed
        wheel_back_right.throttle = 0.1 + speed
    else:
        wheel_front_left.throttle = 0.1 + speed
        wheel_front_right.throttle = 0.1 - speed
        wheel_back_left.throttle = 0.1 + speed
        wheel_back_right.throttle = 0.1 - speed
    
    time.sleep(duration)
    
    # 停止轮子
    wheel_front_left.throttle = 0.1
    wheel_front_right.throttle = 0.1
    wheel_back_left.throttle = 0.1
    wheel_back_right.throttle = 0.1

def robot_action():
    """机器人动作响应"""
    # 移动手臂
    move_arms(left_speed=0.3, right_speed=0.3, duration=0.5)
    time.sleep(0.2)
    move_arms(left_speed=-0.3, right_speed=-0.3, duration=0.5)
    
    # 小幅度前后移动
    move_wheels(forward=True, speed=0.2, duration=0.5)
    time.sleep(0.2)
    move_wheels(forward=False, speed=0.2, duration=0.5)

def speech_to_text(audio_file):
    """将语音转换为文本"""
    try:
        messages = [
            {
                "role": "user",
                "content": [{"audio": audio_file}],
            }
        ]
        
        response = MultiModalConversation.call(model="qwen-audio-asr", messages=messages)
        if response and "output" in response and "choices" in response["output"]:
            text = response["output"]["choices"][0]["message"]["content"][0]["text"]
            print(f"语音识别结果: {text}")
            return text
        else:
            return None
    except Exception as e:
        print(f"语音识别时出错: {e}")
        return None

def text_to_speech(text):
    """将文本转换为语音"""
    try:
        client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        
        audio_string = ""
        completion = client.chat.completions.create(
            model="qwen-omni-turbo",
            messages=[{"role": "user", "content": text}],
            modalities=["text", "audio"],
            audio={"voice": "Cherry", "format": "wav"},
            stream=True,
            stream_options={"include_usage": True},
        )
        
        for chunk in completion:
            if chunk.choices:
                if hasattr(chunk.choices[0].delta, "audio"):
                    try:
                        audio_string += chunk.choices[0].delta.audio["data"]
                    except Exception as e:
                        pass
        
        if audio_string:
            # 解码音频
            wav_bytes = base64.b64decode(audio_string)
            audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
            return audio_np
        else:
            return None
    except Exception as e:
        print(f"文本转语音时出错: {e}")
        return None

def handle_touch():
    """处理触摸事件"""
    print("检测到触摸！执行欢迎动作")
    
    # 创建线程执行表情、声音和动作
    t1 = threading.Thread(target=lambda: show_emotion('happy', loops=2))
    t2 = threading.Thread(target=lambda: play_audio("sounds/hello.wav"))
    t3 = threading.Thread(target=robot_action)
    
    t1.start()
    t2.start()
    t3.start()
    
    t1.join()
    t2.join()
    t3.join()

def handle_voice_interaction():
    """处理语音交互"""
    # 显示正在听的表情
    t1 = threading.Thread(target=lambda: show_emotion('blink', loops=1))
    t1.start()
    
    # 录制音频
    audio_file = record_audio(seconds=5, filename="user_input.wav")
    
    # 显示思考表情
    t1.join()
    t2 = threading.Thread(target=lambda: show_emotion('dizzy', loops=1))
    t2.start()
    
    # 语音识别
    text = speech_to_text(audio_file)
    
    if text:
        # 语音合成
        audio_np = text_to_speech(text)
        
        if audio_np is not None:
            # 显示回答表情并播放回复
            t2.join()
            t3 = threading.Thread(target=lambda: show_emotion('happy', loops=2))
            t3.start()
            
            # 播放合成的语音
            play_audio_from_array(audio_np)
            
            t3.join()
        else:
            # 显示悲伤表情
            t2.join()
            show_emotion('sad', loops=1)
    else:
        # 显示悲伤表情
        t2.join()
        show_emotion('sad', loops=1)

# 主循环
def main():
    print("机器人启动，等待触摸...")
    
    # 显示等待表情
    show_emotion('blink', loops=1)
    
    try:
        while True:
            # 检测触摸
            if lgpio.gpio_read(h, touch_pin) == 1:
                # 先播放欢迎动作
                handle_touch()
                
                # 然后进入语音交互
                handle_voice_interaction()
                
                # 重新显示等待表情
                show_emotion('blink', loops=1)
                
                # 防抖延时
                time.sleep(1)
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("用户中断，程序退出")
    finally:
        # 清理资源
        lgpio.gpiochip_close(h)
        # 停止所有电机
        arm_left.throttle = 0.1
        arm_right.throttle = 0.1
        wheel_front_left.throttle = 0.1
        wheel_front_right.throttle = 0.1
        wheel_back_left.throttle = 0.1
        wheel_back_right.throttle = 0.1

if __name__ == "__main__":
    main()
