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

from threading import Thread
from time import sleep
from helpers.arm import ARM
from helpers.servo import SERVO
from helpers.wheel import WHEEL
import logging

arm = ARM()
servo = SERVO()
wheel = WHEEL()

NOOP, FORWARD, BACKWARD = 0, 1, 2

class Instruction:
    def __init__(self, typ = NOOP, args = None):
        self.typ = typ
        self.args = args if args != None else []

instruction_queue = []
instruction_thread = None
instruction_running = False

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def run(listOfInstructions):
    global instruction_queue
    logging.debug(f"Adding instructions: {listOfInstructions}")
    instruction_queue.extend(listOfInstructions)

def run_instructions():
    global instruction_running
    while instruction_running:
        if len(instruction_queue) > 0:
            instruction = instruction_queue.pop(0)
            logging.debug(f"Processing instruction: {instruction}")
            if instruction.typ == NOOP:
                logging.debug("Executing NOOP instruction")
                pass
            elif instruction.typ == FORWARD:
                logging.debug(f"Executing FORWARD instruction with args: {instruction.args}")
                wheel.straight()
                sleep(instruction.args[0])
                wheel.stop()
            elif instruction.typ == BACKWARD:
                logging.debug(f"Executing BACKWARD instruction with args: {instruction.args}")
                wheel.back()
                sleep(instruction.args[0])
                wheel.stop()
        else:
            logging.debug("Instruction queue is empty, sleeping...")
            sleep(0.1)

def start():
    global instruction_queue, instruction_running, instruction_thread
    if (instruction_thread is not None and instruction_thread.is_alive()):
        logging.debug("Instruction thread is already running")
        return
    logging.debug("Starting instruction thread")
    instruction_thread = Thread(target=run_instructions)
    instruction_running = True
    instruction_thread.start()

def stop():
    global instruction_queue, instruction_running, instruction_thread
    logging.debug("Stopping instruction thread")
    instruction_running = False
    if instruction_thread is not None:
        instruction_thread.join()
    instruction_queue = []
    logging.debug("Instruction thread stopped and queue cleared")
