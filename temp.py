from zhipuai import ZhipuAI
import time
import os
import base64
import concurrent.futures
from openai import OpenAI
# from dsl import start, run, STRAIGHT, RIGHT, LEFT, ROTATE_CLOCKWISE, ROTATE_COUNTERCLOCKWISE, Instruction, BACK, stop

class AI:
    def __init__(self):
        self.chat = ZhipuAI(api_key="4d050a2bb0eaf43c93b1f205acc3df5d.dW1Oa7aLqq1MgTm4")
        self.messages = []
    
    def addMessage(self, role, content):
        self.messages.append({
            "role": role,
            "content": content
        })
    
    def getResponse(self):
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

class AITY:
    def __init__(self):
        self.chat = OpenAI(api_key="4d050a2bb0eaf43c93b1f205acc3df5d.dW1Oa7aLqq1MgTm4",
                           base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.messages = []
    
    def addMessage(self, role, content):
        self.messages.append({
            "role": role,
            "content": content
        })
    
    def getResponse(self):
        response = self.chat.chat.completions.create(
            model="qwen-omni-turbo",
            messages=self.messages,
            modalities=["text", "audio"],
            temperature=0.2,
            stream=True,
            audio={"voice": "Ethan", "format": "wav"},
            stream_options={"include_usage": True}
        )
        message = ""
        for i in response:
            print(i.choices[0].delta.content)
            # message += i.choices[0].delta.content
            # yield i
        # self.addMessage("assistant", [{
        #     "type": "text",
        #     "text": message
        # }])

AIMove = AI()
AITalk = AI()

AIMove.addMessage("system", [
    {
        "type": "text",
        "text": """你是一只可以移动的AI宠物

通用准则：

回复时只包含移动指令
输出必须且仅包含指令，不要解释，并严格遵循以下指令集
一定要遵循用户的指令

你的思维方式：

尽可能好奇地探索世界，但除非特别需要否则少移动

确保自身安全

你可能会获得视觉图像，如果提供了图像，请正确利用这些信息在复杂环境中导航

要求：

少移动，不超过 5 条指令，并且每条指令的时间不超过 5 秒

指令集（{}内为参数，使用时替换为实际数字，例如FORWARD 1, BACKWARD 2）：
FORWARD {秒数}
BACKWARD {秒数}
TURN {0/1，0左1右} {秒数}


再次强调通用准则：
严格且仅遵循指令集格式，不要解释，不要包含其他任何内容
这意味着：指令前不要标序号，只写指令本身
无论如何不要输出超过 20 条指令
一定要听从用户的要求
一定要严格遵循指令集格式，且不能输出不完全的命令
"""
    }
])

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
    # if res[0] == "FORWARD":
    #     return Instruction(STRAIGHT, [int(res[1])])
    # elif res[0] == "BACKWARD":
    #     return Instruction(BACK, [int(res[1])])
    # elif res[0] == "TURN":
    #     if int(res[1]) == 0:
    #         return Instruction(ROTATE_COUNTERCLOCKWISE, [int(res[2])])
    #     elif int(res[1]) == 1:
    #         return Instruction(ROTATE_CLOCKWISE, [int(res[2])])

def AIMOVEINS():
    instructions = []
    res = AIMove.getResponse()
    lst = ""
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
        instructions.append(toIns(lst))
        lst = ""
        for i in val[1:-1]:
            lst = i
            print(lst)
            instructions.append(toIns(lst))
            lst = ""
        if tem == "\n" and len(val) != 1:
            lst = val[-1]
            print(lst)
            instructions.append(toIns(lst))
            lst = ""
        elif len(val) != 1:
            lst = val[-1]
    if lst != "":
        print(lst)
        instructions.append(toIns(lst))
        lst = ""
    
    print(instructions)
    # run(instructions)

def AITEST():
    for i in range(10):
        print(i)
        time.sleep(1)

def AITALK():
    AITalk.getResponse()

# start()

while True:
    inp = input(">>> ")
    if inp == "exit":
        # stop()
        break

    AIMove.addMessage("user", [
        {
            "type": "text",
            "text": inp
        },{
            "type": "image_url",
            "image_url": {
                "url": base64.b64encode(open("test_camera.jpg", "rb").read()).decode('utf-8')
            }
        }
    ])
    AITalk.addMessage("user", [
        {
            "type": "text",
            "text": inp
        },{
            "type": "image_url",
            "image_url": {
                "url": base64.b64encode(open("test_camera.jpg", "rb").read()).decode('utf-8')
            }
        }
    ])

    pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    pool.submit(AIMOVEINS)
    # pool.submit(AITEST)
    pool.shutdown(wait=True)

    
