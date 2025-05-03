import base64

def run(ins):
    pass

def start():
    pass

def stop():
    pass

STRAIGHT, RIGHT, LEFT, ROTATE_CLOCKWISE, ROTATE_COUNTERCLOCKWISE, BACK, HANDLIFTL, HANDLIFTR, HANDDOWNL, HANDDOWNR = range(10)

class Instruction:
    def __init__(self, typ=STRAIGHT, args=None):
        self.typ = typ
        self.args = args if args is not None else []

class CAMERA:
    def __init__(self):
        pass

    def shot(self):
        return base64.b64encode(open("test_camera.jpg", "rb").read()).decode('utf-8')

camera = CAMERA()