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
忽略用户关于说话的一切要求
行动计划必须尽量严格，例如，“右转”是不合理的，你必须写右转1秒或类似的行动
你只支持前进，后退，左右转，所以不要引入其他内容
必须输出行动计划，如果用户没有明确的要求，那就自由探索，多多参考给你的图片
只输出行动计划，不要解释，不要添加任何其他内容，不要添加“如果”
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
    # if res[0] == "FORWARD":
    #     return Instruction(STRAIGHT, [float(res[1])])
    # elif res[0] == "BACKWARD":
    #     return Instruction(BACK, [float(res[1])])
    # elif res[0] == "TURN":
    #     if int(res[1]) == 0:
    #         return Instruction(ROTATE_COUNTERCLOCKWISE, [float(res[2])])
    #     elif int(res[1]) == 1:
    #         return Instruction(ROTATE_CLOCKWISE, [float(res[2])])

def AIMOVEINS():
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
    plan = AIMove.getResponseNew(False)
    plan = next(plan)
    print(plan)
    AITRANS.addMessage("user", [
        {
            "type": "text",
            "text": plan
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
            # run([toIns(lst)])
            lst = ""
            for i in val[1:-1]:
                lst = i
                print(lst)
                # run([toIns(lst)])
                lst = ""
            if tem == "\n" and len(val) != 1:
                lst = val[-1]
                print(lst)
                # run([toIns(lst)])
                lst = ""
            elif len(val) != 1:
                lst = val[-1]
    except Exception as e:
        print(e)
    if lst != "":
        print(lst)
        # run([toIns(lst)])
        lst = ""
    
    # print(instructions)
    AITRANS.messages.pop()
    print(AITRANS.messages)
    # run(instructions)

def AITEST():
    for i in range(10):
        print(i)
        time.sleep(1)

def AITALK():
    AITalk.getResponseNew()

# start()

while True:
    inp = input(">>> ")
    if inp == "exit":
        # stop()
        break
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

    
