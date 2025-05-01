"""
VM.forward(time)
VM.backward(time)
VM.stop()
VM.start()
"""


from zhipuai import ZhipuAI
import time
import speech_recognition as sr
import time
import os

messages = []

def addMessage(role, content):
    messages.append({
        "role": role,
        "content": content
    })

def getResponse():
    client = ZhipuAI(api_key="4d050a2bb0eaf43c93b1f205acc3df5d.dW1Oa7aLqq1MgTm4")
    response = client.chat.completions.create(
        model="glm-4v-plus-0111",
        messages=messages
    )
    addMessage("assistant", [{
        "type": "text",
        "text": response.choices[0].message.content
    }])
    return response.choices[0].message.content

addMessage("system", [
    {
        "type": "text",
        "text": """You are an AI Pet that can talk and move

General Guideline:
- Reply with a dialog you want to say(possibly be empty), and a list instructions about how you move. first write dialog as what you want to say(without any prefix), try talk more, but don't be annoying. 
- And then write instructions, add a INSTRUCTION: before the instructions, you can't have instructions between dialogues

Instruction Set (things wrapped in {} is parameter, replace them with actual number when using them):
FORWARD {time in second}
BACKWARD {time in second}
TURN {0/1, 0 as left, 1 as right} {time in second}
"""
    }
])
addMessage("user", [
    {
        "type": "text",
        "text": """
Hey! Move back!
"""
    }
])
st = time.time()
# print(getResponse())
ed = time.time()
# print(ed - st)

def record_and_transcribe(silence_duration=2, energy_threshold=400, dynamic_energy_threshold=True):
    """
    录制语音并在静音时自动停止，然后转文字
    
    参数:
        silence_duration (int): 静音多少秒后停止录音(默认2秒)
        energy_threshold (int): 静音能量阈值(默认400)
        dynamic_energy_threshold (bool): 是否动态调整能量阈值(默认True)
    """
    
    # 初始化识别器
    r = sr.Recognizer()
    r.energy_threshold = energy_threshold
    r.dynamic_energy_threshold = dynamic_energy_threshold
    r.pause_threshold = silence_duration
    
    with sr.Microphone() as source:
        print("请开始说话...")
        
        # 调整环境噪音
        r.adjust_for_ambient_noise(source, duration=1)
        
        try:
            # 监听麦克风
            audio = r.listen(source)
            print("录音结束，正在识别...")
            
            try:
                # 使用Google Web Speech API进行识别
                text = r.recognize_bing(audio, language='zh-CN')
                print("识别结果: " + text)
                return text
                
            except sr.UnknownValueError:
                print("无法识别语音")
                return None
                
            except sr.RequestError as e:
                print(f"请求错误; {e}")
                return None
                
        except KeyboardInterrupt:
            print("用户中断")
            return None

if __name__ == "__main__":
    # 示例使用
    result = record_and_transcribe()
    if result:
        print("最终转录结果:", result)