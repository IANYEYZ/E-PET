NOOP, FORWARD = 0, 1

class Instruction:
    def __init__(self, typ = NOOP, args = None):
        self.typ = typ
        self.args = args if args != None else []

def run(listOfInstructions):
    # We need that
    pass