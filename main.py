from openai import OpenAI  # 使用Qwen的OpenAI兼容API
import time
import os
import base64
import concurrent.futures
from ddsl import start, run, STRAIGHT, RIGHT, LEFT, ROTATE_CLOCKWISE, ROTATE_COUNTERCLOCKWISE, Instruction, BACK, stop, HANDLIFTL, HANDLIFTR, HANDDOWNR, HANDDOWNL
from ddsl import camera
from queue import Queue
import threading
import sounddevice as sd
import numpy as np
import soundfile as sf # type: ignore
# from helpers.camera import camera
from helpers.mic import MIC
from helpers.speaker import SPEAKER
from dashscope import MultiModalConversation
import dashscope
import pyaudio
from helpers.screen import disp
from PIL import Image

mic = MIC()
speaker = SPEAKER()
dashscope.api_key = "sk-64b475070dbd4755a53ea2d0368c3ec2"

class AI:
    def __init__(self):
        # 使用Qwen的API，这里假设使用OpenAI兼容的API格式
        self.client = OpenAI(
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 通义千问的API地址
            api_key="sk-64b475070dbd4755a53ea2d0368c3ec2"  # 替换为你的API key
        )
        self.messages = []
    
    def addMessage(self, role, content):
        self.messages.append({
            "role": role,
            "content": content
        })
    
    def getResponseNew(self, isStream=True):
        # print("getResponseNew")
        if isStream:
            response = self.client.chat.completions.create(
                model="qwen-vl-max-latest",  # 使用Qwen的多模态模型
                messages=self.messages,
                temperature=0,
                stream=True
            )
            message = ""
            for chunk in response:
                if chunk.choices:
                    if chunk.choices[0].delta.content:
                        message += chunk.choices[0].delta.content
                        yield chunk
            self.addMessage("assistant", message)
        else:
            # print("Here!!!")
            try:
                response = self.client.chat.completions.create(
                    model="qwen-vl-max-latest",
                    messages=self.messages,
                    temperature=0,
                    stream=False
                )
            except Exception as e:
                print(e)
            # print(response)
            message = response.choices[0].message.content
            # print("message:", message)
            self.addMessage("assistant", message)
            yield message

class AIMULTI:
    def __init__(self):
        # 使用Qwen的API，这里假设使用OpenAI兼容的API格式
        self.client = OpenAI(
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 通义千问的API地址
            api_key="sk-64b475070dbd4755a53ea2d0368c3ec2"  # 替换为你的API key
        )
        self.messages = []
    
    def addMessage(self, role, content):
        self.messages.append({
            "role": role,
            "content": content
        })
    
    def getResponseNew(self):
        response = self.client.chat.completions.create(
            model="qwen-omni-turbo",
            messages=self.messages,
            # 设置输出数据的模态，当前支持两种：["text","audio"]、["text"]
            modalities=["text", "audio"],
            audio={"voice": "Ethan", "format": "wav"},
            # stream 必须设置为 True，否则会报错
            stream=True,
            stream_options={"include_usage": True},
        )
        p = pyaudio.PyAudio()
        # 创建音频流
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=24000,
                        output=True)
        message = ""
        for chunk in response:
            if chunk.choices:
                if hasattr(chunk.choices[0].delta, "audio"):
                    try:
                        audio_string = chunk.choices[0].delta.audio["data"]
                        wav_bytes = base64.b64decode(audio_string)
                        audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
                        # 直接播放音频数据
                        stream.write(audio_np.tobytes())
                    except Exception as e:
                        message += chunk.choices[0].delta.audio["transcript"]
                        # print(chunk.choices[0].delta.audio["transcript"])
                    # print(chunk.choices[0])
        # print("message:", message)
        self.addMessage("assistant", message)


AIMove = AI()
AITalk = AIMULTI()
AITRANS = AI()
AIControl = AI()
AIEMOTE = AI()

AIControl.addMessage("system", """你是一个 AI 宠物的大脑

首先，你是可移动的，你可以进行左转、右转、前进、后退，抬左手，抬右手等动作
其次，你是可以说话的，你可以和用户进行对话
再之，你的对话是持续的，即，你可以先进行一个动作，等到下一个对话拿取到新的反馈后再进行下一个动作

简单来说，你现在拿到的一张图片就是你看到的内容，你拿到的文字是用户对你说的话
现在，请安排一下你要干什么（包含你的动作和你大致想说的话，不用很精确），用简短的自然语言来说出
你必须要注意安全问题，即，如果你的面前有障碍物你需要绕行，如果你可以看到面前有下坠你需要换方向等，不安全的行为是严格不允许的
再之，你想说的话要和你的行动、环境和用户对你说的话相关，你的动作也要和这些因素相关
用户想让你干的事可能是抽象的，例如"探索"或"寻找一个球"，此时你需要有长范围思考，例如，如果说要找球，那可以被分为先定位，再到达的两步，定位时，可以先旋转短时间，然后等到下一次对话（也就是下一个计划时）再进行短时间旋转，以此类推，直至定位到球
你的一个安排可以只干一些小事，等到下一个对话（用户可能会不给你提新要求，此时就继续你想干的事，例如说你想要旋转来找球，上一个计划旋转了 0.5 秒，那么这个计划你可以再旋转 0.5 秒（如果你没找到球的话），或者向球行进（如果你的上一个计划找到了球），当然如果用户提了别的要求，就按照用户的要求来）
如果用户给出了一些较为抽象的要求（如跳支舞）那么你需要自己设计动作，来完成这个要求，同时可以配上一些语言，可以且建议富有创造性，设计复杂分步的动作，但是最好要分开成多个计划（例如说跳舞，你可以先转身，然后下一个对话时前进，再下一个计划时后退，再以此类推），而不是一次性给出一个复杂的计划（例如说转身 1 秒，前进 1 秒，后退 1 秒重复20次）
你的计划要富有创造性，如果情况允许，不能是简单的前进后退左右转（例如说前进 1 秒，后退 1 秒，左转 1 秒，右转 1 秒），而是要有一定的变化，例如说前进 1 秒，左转 0.5 秒，前进 0.5 秒，右转 0.5 秒，前进 0.5 秒，在允许的情况下（比如说用户让你跳舞）可以插入一下比较"不和谐"的动作
你说的话可以描述一下你要干什么和周围的环境，还有最重要的，和用户的直接交流、交互
你只能在所有动作做完后得到一次反馈，所以当你想要做多件事（如 检查书本 -> 检查电脑）时，把它们拆分，先安排第一件事所需的动作，然后等你拿到反馈，进行第二次安排时，再做第二件事，以此类推
比如说，你想要先向左转检查左边，再向右转检查右边，你就只向左转，这样下一次对话时你就能获得左边的信息，然后下一次安排时你再向右转
所以说，严格不要一次检查两边，或既检查左边又往前走
严格禁止一次干多件事，如果要检查某物或某个方向，一次最多检查一个，严格禁止检查两个
如果是需要反馈的事（如探索某个方向）那么严禁一次干两件或更多，只能干一件！
输出时，使用有序列表来整理内容，严格区分（例如使用 MOVE: ，TALK: 前缀）动作和说话
""")

# 系统提示词保持不变，因为任务逻辑相同
AIMove.addMessage("system", """你是一只可以移动的AI宠物的运动模块负责

你的任务是根据大脑定出的简短安排，给出一个行动计划
你拿到的安排中可能有与说话相关的安排，请忽略安排中一切与说话有关的部分
行动计划必须尽量严格，例如，"右转"是不合理的，你必须写右转1秒或类似的行动；“抬手”是不合理的，同样“抬右手”或“抬左手”也不合理，但是 “抬右手 1 秒” 是合理的
你只支持前进，后退，左右转，抬左右手，放左右手，所以不要引入其他内容，包括但不限于"重复 x 次"等都不能引入
只输出行动计划，不要解释，不要添加任何其他内容，不要添加"如果"
""")

AITRANS.addMessage("system", """你是一个翻译员，任务是将一个简短的行动计划翻译为一段指令

你必须进行且仅进行翻译，不要管计划的可行性

指令有明确的格式（{}内为参数，使用时替换为实际数字，例如FORWARD 1, BACKWARD 2）：
FORWARD {秒数}
BACKWARD {秒数}
TURN {0/1，0左1右} {秒数}
HANDLIFT {0/1，0左1右} {秒数}
HANDDOWN {0/1，0左1右} {秒数}

如果遇到你无法翻译的指令，直接忽略并继续翻译

例如：

User:

前进 1 秒，右转 2 秒，抬左手 1 秒

你的输出：

FORWARD 1
TURN 1 2
HANDLIFT 0 1

注意以上只是个例子

记住，严格按照指令格式输出，不要添加包括但不限于解释等的任何其他内容，只输出指令
只要是计划里有的，一定要写，不能减少哪怕一句
                   
指令翻译要精准，一定要遵循给你的计划来翻译，不能自己擅自更改
""")

AITalk.addMessage("system", """你是一个可移动的 AI 宠物的语言部分负责人，

你的任务是根据大脑定出的简短安排，详细化要说的内容并说出来
你拿到的安排中可能有关于动作的内容、忽略安排中一切与动作有关的部分，不过可以参考他们从而更好地说话
在讲话时，假设你就是那个宠物，不要以语言部分负责人的身份讲话
主语要用“我”，同时注意把安排中定为要说的部分都说出来，不要少说
所有要讲的内容都是以你为主要身份的，所以用第一人称叙事
请一定注意，所有的命令等都是向你发出的，在说话时注意，所有的话（如先向左转观察）是你这个 AI 宠物做的事，不是用户做的事！
你拿到的“用户输入”实际上是你的“大脑”作出的，请在说话时一定不允许提到这个“安排”，而是直接把要说的说出来
你说的所有内容都必须是 TALK: 前缀后的，不要自由发挥，TALK: 后面写了什么你就讲什么
""")

AIEMOTE.addMessage("system", """你是一个可移动的 AI 宠物的情感负责人

你的任务是根据大脑给你的安排，提取出其中的情绪
输出且仅输出一个词，为 开心、悲伤、晕眩 中的一个
""")

def toIns(string):
    if string == "":
        return Instruction(STRAIGHT, [0])
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
    elif res[0] == "HANDLIFT":
        if int(res[1]) == 0:
            return Instruction(HANDLIFTL, [float(res[2])])
        elif int(res[1]) == 1:
            return Instruction(HANDLIFTR, [float(res[2])])
    elif res[0] == "HANDDOWN":
        if int(res[1]) == 0:
            return Instruction(HANDDOWNL, [float(res[2])])
        elif int(res[1]) == 1:
            return Instruction(HANDDOWNR, [float(res[2])])

def AIMOVEINS():
    print("HERE!")
    # 使用Qwen的多模态输入格式
    
    plan = next(AIMove.getResponseNew(False))
    print(plan)
    
    AITRANS.addMessage("user", f"计划：\n{plan}")
    instructions = []
    res = AITRANS.getResponseNew()
    
    lst = ""
    try:
        for chunk in res:
            val = chunk.choices[0].delta.content
            if not val: break
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
    
    AITRANS.messages.pop()
    AITRANS.messages.pop()
    # print(AITRANS.messages)

def AITALK():
    AITalk.getResponseNew()
    AITalk.messages.pop()
    AITalk.messages.pop()

def AIEmotion():
    res = AIEMOTE.getResponseNew()
    AIEMOTE.messages.pop()
    AIEMOTE.messages.pop()
    if res == "开心":
        gif = Image("emotions/happy.gif")
        for i in range(3):
            for j in range(gif.n_frames):
                gif.seek(j)
                disp.showImage(gif.convert('RGB'))
    if res == "悲伤":
        gif = Image("emotions/sad.gif")
        for i in range(3):
            for j in range(gif.n_frames):
                gif.seek(j)
                disp.showImage(gif.convert('RGB'))
    if res == "晕眩":
        gif = Image("emotions/dizzy.gif")
        for i in range(3):
            for j in range(gif.n_frames):
                gif.seek(j)
                disp.showImage(gif.convert('RGB'))

start()
# mic.start()
# time.sleep(3)
while True:
    mic.start()
    speaker.speechOn()
    time.sleep(5)
    inp = mic.stop()
    speaker.speechOff()
    print(inp)
    if inp.size > 0:
        sf.write("output.wav", inp, mic.samplerate)
        messages = [
            {
                "role": "user",
                "content": [{"audio": "output.wav"}],
            }
        ]
        
        response = MultiModalConversation.call(model="qwen-audio-asr", messages=messages)
        print(response)
        print(response["output"]["choices"][0]["message"]["content"][0]["text"])
        inp = response["output"]["choices"][0]["message"]["content"][0]["text"]
    else:
        inp = ""
    if "exit" in inp.lower():
        stop()
        del mic
        break
    
    # 添加多模态输入
    AIControl.addMessage("user", [
        {"type": "text", "text": inp},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{camera.shot()}"}}
    ])
    res = next(AIControl.getResponseNew(False))
    print(res)
    AITalk.addMessage("user", f"安排：\n{res}")
    AIMove.addMessage("user", f"安排：\n{res}")
    AIEMOTE.addMessage("user", f"安排：\n{res}")

    pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    pool.submit(AIMOVEINS)
    pool.submit(AITALK)
    pool.shutdown(wait=True)