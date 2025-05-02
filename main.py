from zhipuai import ZhipuAI # type: ignore
import time
import os
import base64
import concurrent.futures
from openai import OpenAI # type: ignore
from ddsl import start, run, STRAIGHT, RIGHT, LEFT, ROTATE_CLOCKWISE, ROTATE_COUNTERCLOCKWISE, Instruction, BACK, stop
from ddsl import camera
from queue import Queue
import threading
import sounddevice as sd # type: ignore
import speech_recognition as sr # type: ignore
import numpy as np
import soundfile as sf # type: ignore
# from helpers.camera import camera

class MIC:
    def __init__(self, samplerate=16000, channels=1, dtype='float32'):
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

mic = MIC()

class AI:
    def __init__(self):
        self.chat = ZhipuAI(api_key="4d050a2bb0eaf43c93b1f205acc3df5d.dW1Oa7aLqq1MgTm4")
        self.messages = []
    
    def addMessage(self, role, content):
        self.messages.append({
            "role": role,
            "content": content
        })
    
    def getResponseNew(self, isStream = True):
        # print(isStream)
        if isStream:
            response = self.chat.chat.completions.create(
                model="glm-4v-plus-0111",
                messages=self.messages,
                temperature=0,
                seed=int(time.time()),
                stream=True
            )
            message = ""
            for i in response:
                message += i.choices[0].delta.content
                yield i
            self.addMessage("assistant", [{
                "type": "text",
                "text": message
            }])
        else:
            response = self.chat.chat.completions.create(
                model="glm-4v-plus-0111",
                messages=self.messages,
                temperature=0,
                seed=int(time.time())
            )
            message = response.choices[0].message.content
            self.addMessage("assistant", [{
                "type": "text",
                "text": message
            }])
            yield message

AIMove = AI()
AITalk = AI()
AITRANS = AI()

AIMove.addMessage("system", [
    {
        "type": "text",
        "text": """你是一只可以移动的AI宠物

你的任务是根据当前的情况（给你的图片），和用户的要求（可能有可能没有），给出一个简短的行动计划
行动计划越短越好
例如，如果用户让你找到球，那么你最好小范围旋转，并且在下一次继续小范围旋转，直到找到球
用户的需求可能是抽象的，例如“探索”或“寻找一个球”，此时你需要有长范围思考，例如，如果说要找球，那可以被分为先定位，再到达的两步，定位时，可以先旋转短时间，然后等到下一次对话（也就是下一个计划时）再进行短时间旋转，以此类推，直至定位到球
你的一个计划可以只干一些小事，等到下一个对话（用户可能会不给你提新要求，此时就继续你想干的事，例如说你想要旋转来找球，上一个计划旋转了 0.5 秒，那么这个计划你可以再旋转 0.5 秒（如果你没找到球的话），或者向球行进（如果你的上一个计划找到了球），当然如果用户提了别的要求，就按照用户的要求来）
如果用户给出了一些较为抽象的要求（如跳支舞）那么你需要自己设计动作，来完成这个要求，可以且建议富有创造性，设计复杂分步的动作，但是最好要分开成多个计划（例如说跳舞，你可以先转身，然后下一个对话时前进，再下一个计划时后退，再以此类推），而不是一次性给出一个复杂的计划（例如说转身 1 秒，前进 1 秒，后退 1 秒重复20次）
你的计划要富有创造性，如果情况允许，不能是简单的前进后退左右转（例如说前进 1 秒，后退 1 秒，左转 1 秒，右转 1 秒），而是要有一定的变化，例如说前进 1 秒，左转 0.5 秒，前进 0.5 秒，右转 0.5 秒，前进 0.5 秒，在允许的情况下（比如说用户让你跳舞）可以插入一下比较“不和谐”的动作
忽略用户关于说话的一切要求
行动计划必须尽量严格，例如，“右转”是不合理的，你必须写右转1秒或类似的行动
你只支持前进，后退，左右转，所以不要引入其他内容
必须输出行动计划，如果用户没有明确的要求，那就自由探索，多多参考给你的图片
只输出行动计划，不要解释，不要添加任何其他内容，不要添加“如果”
若用户没有要求且你没有之前的计划，返回空计划
"""
    }
])
AITRANS.addMessage("system", [
    {
        "type": "text",
        "text": """你是一个翻译员，任务是将一个简短的行动计划翻译为一段指令

你必须进行且仅进行翻译，不要管计划的可行性

指令有明确的格式（{}内为参数，使用时替换为实际数字，例如FORWARD 1, BACKWARD 2）：
FORWARD {秒数}
BACKWARD {秒数}
TURN {0/1，0左1右} {秒数}

如果遇到你无法翻译的指令，直接忽略并继续翻译

例如：

User:

前进1秒，右转两秒

你的输出：

FORWARD 1
TURN 1 2

记住，严格按照指令格式输出，不要添加包括但不限于解释等的任何其他内容，只输出指令
"""
}])

# AIMove.addMessage("user", [
#     {
#         "type": "text",
#         "text": "Expore freely!"
#     },{
#         "type": "image_url",
#         "image_url": {
#             "url": base64.b64encode(open("test_camera.jpg", "rb").read()).decode('utf-8')
#         }
#     }
# ])
AITalk.addMessage("system", [
    {
        "type": "text",
        "text": """You are an AI Pet that can talk

General Guideline:
- Reply in a "pet-ty" way, just like a e-pet
- You maybe given an image, if it's given, you may use the information to talk better, but it's NOT necessary and shouldn't be used too much
"""
    }
])

def toIns(string):
    res = string.split(" ")
    if res[0] == "FORWARD":
        return Instruction(STRAIGHT, [float(res[1])])
    elif res[0] == "BACKWARD":
        return Instruction(BACK, [float(res[1])])
    elif res[0] == "TURN":
        if int(res[1]) == 0:
            return Instruction(ROTATE_COUNTERCLOCKWISE, [float(res[2])])
        elif int(res[1]) == 1:
            return Instruction(ROTATE_CLOCKWISE, [float(res[2])])

def AIMOVEINS():
    AIMove.addMessage("user", [
        {
            "type": "text",
            "text": f"""用户要求：
{inp}"""
        },{
            "type": "image_url",
            "image_url": {
                "url": camera.shot()
            }
        }
    ])
    plan = AIMove.getResponseNew(False)
    plan = next(plan)
    print(plan)
    AITRANS.addMessage("user", [
        {
            "type": "text",
            "text": f"""计划：
{plan}"""
        }
    ])
    instructions = []
    res = AITRANS.getResponseNew()
    lst = ""
    try:
        for chunk in res:
            val = chunk.choices[0].delta.content
            if (val == ""): break
            tem = val[-1]
            val = val.splitlines()
            if len(val) == 1 and tem != "\n":
                lst += val[0]
                continue
            lst = lst + val[0]
            print(lst)
            run([toIns(lst)])
            lst = ""
            for i in val[1:-1]:
                lst = i
                print(lst)
                run([toIns(lst)])
                lst = ""
            if tem == "\n" and len(val) != 1:
                lst = val[-1]
                print(lst)
                run([toIns(lst)])
                lst = ""
            elif len(val) != 1:
                lst = val[-1]
    except Exception as e:
        print(e)
    if lst != "":
        print(lst)
        run([toIns(lst)])
        lst = ""
    
    # print(instructions)
    AITRANS.messages.pop()
    # print(AITRANS.messages)
    # run(instructions)

def AITEST():
    for i in range(10):
        print(i)
        time.sleep(1)

def AITALK():
    AITalk.getResponseNew()

start()
recognizer = sr.Recognizer()
mic.start()

while True:
    # inp = input(">>> ")
    inp = mic.stop()
    if inp.size > 0:
        sf.write("output.wav", inp, mic.samplerate)
        client = ZhipuAI(api_key="4d050a2bb0eaf43c93b1f205acc3df5d.dW1Oa7aLqq1MgTm4")
        with open("output.wav", "rb") as f:
            transcriptResponse = client.audio.transcriptions.create(
                model="glm-asr",
                file=f,
                stream=False
            )
        print(transcriptResponse.text)
        inp = transcriptResponse.text
    else:
        inp = ""
    mic.start()
    if "exit" in inp.lower():
        stop()
        mic.stop()
        del mic
        break
    AITalk.addMessage("user", [
        {
            "type": "text",
            "text": inp
        },{
            "type": "image_url",
            "image_url": {
                "url": camera.shot()
            }
        }
    ])
    # time.sleep(5)

    pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    pool.submit(AIMOVEINS)
    # pool.submit(AITEST)
    pool.shutdown(wait=True)

    
