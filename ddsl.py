def run():
    pass

def start():
    pass

def stop():
    pass

STRAIGHT, RIGHT, LEFT, ROTATE_CLOCKWISE, ROTATE_COUNTERCLOCKWISE, BACK = range(6)

class Instruction:
    def __init__(self, typ=STRAIGHT, args=None):
        self.typ = typ
        self.args = args if args is not None else []