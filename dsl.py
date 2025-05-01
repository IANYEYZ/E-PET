from threading import Thread
from helpers.arm import ARM
from helpers.servo import SERVO
from helpers.wheel import WHEEL

arm = ARM()
servo = SERVO()
wheel = WHEEL()

NOOP, FORWARD = 0, 1

class Instruction:
    def __init__(self, typ = NOOP, args = None):
        self.typ = typ
        self.args = args if args != None else []

instruction_queue = []
instruction_thread = None
instruction_running = False

def run(listOfInstructions):
    global instruction_queue
    instruction_queue.extend(listOfInstructions)

def run_instructions():
    while instruction_running:
        if len(instruction_queue) > 0:
            instruction = instruction_queue.pop(0)
            if instruction.typ == NOOP:
                pass
            elif instruction.typ == FORWARD:
                wheel.straight()
                sleep(instruction.args[0])
                wheel.stop()
        else:
            time.sleep(0.1)

def start():
    global instruction_queue
    global instruction_thread
    if (instruction_thread is not None and instruction_thread.is_alive()):
        return
    instruction_thread = Thread(target=run_instructions)
    instruction_running = True
    instruction_thread.start()

def stop():
    global instruction_queue, instruction_thread
    instruction_running = False
    if instruction_thread is not None:
        instruction_thread.join()
    instruction_queue = []
