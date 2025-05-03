import time
from . import lcdconfig

class LCD_2inch(lcdconfig.RaspberryPi):

    width = 240
    height = 320 

    def command(self, cmd):
        self.digital_write(self.DC_PIN, 0)  # LOW
        self.spi_writebyte([cmd])

    def data(self, val):
        self.digital_write(self.DC_PIN, 1)  # HIGH
        self.spi_writebyte([val])

    def reset(self):
        """Reset the display"""
        self.digital_write(self.RST_PIN, 1)
        time.sleep(0.01)
        self.digital_write(self.RST_PIN, 0)
        time.sleep(0.01)
        self.digital_write(self.RST_PIN, 1)
        time.sleep(0.01)
        
    def Init(self):
        """Initialize display"""  
        self.module_init()
        self.reset()

        self.command(0x36)
        self.data(0x00) 

        self.command(0x3A) 
        self.data(0x05)

        self.command(0x21) 

        self.command(0x2A)
        self.data(0x00)
        self.data(0x00)
        self.data(0x01)
        self.data(0x3F)

        self.command(0x2B)
        self.data(0x00)
        self.data(0x00)
        self.data(0x00)
        self.data(0xEF)

        self.command(0xB2)
        self.data(0x0C)
        self.data(0x0C)
        self.data(0x00)
        self.data(0x33)
        self.data(0x33)

        self.command(0xB7)
        self.data(0x35) 

        self.command(0xBB)
        self.data(0x1F)

        self.command(0xC0)
        self.data(0x2C)

        self.command(0xC2)
        self.data(0x01)

        self.command(0xC3)
        self.data(0x12)   

        self.command(0xC4)
        self.data(0x20)

        self.command(0xC6)
        self.data(0x0F) 

        self.command(0xD0)
        self.data(0xA4)
        self.data(0xA1)

        self.command(0xE0)
        self.data(0xD0)
        self.data(0x08)
        self.data(0x11)
        self.data(0x08)
        self.data(0x0C)
        self.data(0x15)
        self.data(0x39)
        self.data(0x33)
        self.data(0x50)
        self.data(0x36)
        self.data(0x13)
        self.data(0x14)
        self.data(0x29)
        self.data(0x2D)

        self.command(0xE1)
        self.data(0xD0)
        self.data(0x08)
        self.data(0x10)
        self.data(0x08)
        self.data(0x06)
        self.data(0x06)
        self.data(0x39)
        self.data(0x44)
        self.data(0x51)
        self.data(0x0B)
        self.data(0x16)
        self.data(0x14)
        self.data(0x2F)
        self.data(0x31)

        self.command(0x21)
        self.command(0x11)
        self.command(0x29)

    def SetWindows(self, Xstart, Ystart, Xend, Yend):
        # Set X coordinates
        self.command(0x2A)
        self.data(Xstart >> 8)
        self.data(Xstart & 0xff)
        self.data(Xend >> 8)
        self.data((Xend - 1) & 0xff)

        # Set Y coordinates
        self.command(0x2B)
        self.data(Ystart >> 8)
        self.data(Ystart & 0xff)
        self.data(Yend >> 8)
        self.data((Yend - 1) & 0xff)

        self.command(0x2C)    
        
    def ShowImage(self, Image, Xstart=0, Ystart=0):
        """Display PIL image on screen."""
        imwidth, imheight = Image.size
        img = self.np.asarray(Image)

        if imwidth == self.height and imheight == self.width:
            pix = self.np.zeros((self.width, self.height, 2), dtype=self.np.uint8)
            pix[..., [0]] = self.np.add(self.np.bitwise_and(img[..., [0]], 0xF8), self.np.right_shift(img[..., [1]], 5))
            pix[..., [1]] = self.np.add(self.np.bitwise_and(self.np.left_shift(img[..., [1]], 3), 0xE0), self.np.right_shift(img[..., [2]], 3))
            pix = pix.flatten().tolist()

            self.command(0x36)
            self.data(0x70)
            self.SetWindows(0, 0, self.height, self.width)
        else:
            pix = self.np.zeros((imheight, imwidth, 2), dtype=self.np.uint8)
            pix[..., [0]] = self.np.add(self.np.bitwise_and(img[..., [0]], 0xF8), self.np.right_shift(img[..., [1]], 5))
            pix[..., [1]] = self.np.add(self.np.bitwise_and(self.np.left_shift(img[..., [1]], 3), 0xE0), self.np.right_shift(img[..., [2]], 3))
            pix = pix.flatten().tolist()

            self.command(0x36)
            self.data(0x00)
            self.SetWindows(0, 0, self.width, self.height)

        self.digital_write(self.DC_PIN, 1)  # HIGH
        for i in range(0, len(pix), 4096):
            self.spi_writebyte(pix[i:i + 4096])

    def clear(self):
        """Clear the display"""
        _buffer = [0xFF] * (self.width * self.height * 2)
        self.SetWindows(0, 0, self.height, self.width)
        self.digital_write(self.DC_PIN, 1)  # HIGH
        for i in range(0, len(_buffer), 4096):
            self.spi_writebyte(_buffer[i:i + 4096])

    def setPixel(self, x, y, color):
        """Set a pixel on the display"""
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        self.SetWindows(x, y, x + 1, y + 1)
        self.digital_write(self.DC_PIN, 1)
        self.spi_writebyte([(color >> 8) & 0xFF, color & 0xFF])
