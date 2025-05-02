from zhipuai import ZhipuAI
import time
import speech_recognition as sr
import time
import os
import base64
import concurrent.futures
from openai import OpenAI

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
            temperature=0.2,
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
        "text": """You are an AI Pet that can move

General Guideline:
- Reply with instructions about how you move.
- OUTPUT with and ONLY with INSTRUCTIONS, no explanation, and STRICTLY FOLLOW the Instruction Set below

Your Mindset:
- Explore the world, as curious as possible, but move less unless specifically required
- Keep yourself safe
- You MAYBE given a image as what you see, if it's given, use the information correctly to navigate through the complex environment

Requiration:
- MOVE LESS, NO MORE THAN 20 INSTRUCTIONS, but you can move longer time if you want to or need to

Example:
1. FORWARD 1
2. TURN 1 1
3. FORWARD 1
4. TURN 0 1
5. FORWARD 1

THE EXAMPLE ABOVE IS WRONG since you DID NOT FOLLOW the Instruction Set

Example:
FORWARD 11
TURN 1 1
FORWARD 11
TURN 0 1
FORWARD 11

THE EXAMPLE ABOVE IS CORRECT since you FOLLOWED the Instruction Set
NOTE: all the examples are just examples, for reference, DO NOT COPY THEM

Instruction Set (things wrapped in {} is parameter, replace them with actual number when using them, for example, FORWARD 1, BACKWARD 2):
FORWARD {time in second}
BACKWARD {time in second}
TURN {0/1, 0 as left, 1 as right} {time in second}

General Guideline again:
Follow the Instruction Set strictly, and ONLY the Instruction Set, no explanation, and no other things
That means, no number before instructions, ONLY the instructions themselves
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

def AIMOVEINS():
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
        lst = ""
        for i in val[1:-1]:
            lst = i
            print(lst)
            lst = ""
        if tem == "\n" and len(val) != 1:
            lst = val[-1]
            print(lst)
            lst = ""
        elif len(val) != 1:
            lst = val[-1]
    if lst != "":
        print(lst)
        lst = ""

def AITEST():
    for i in range(10):
        print(i)
        time.sleep(1)

def AITALK():
    AITalk.getResponse()

while True:
    inp = input(">>> ")
    if inp == "exit":
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

    
