from micropython import const
import framebuf

# commands
CMD_SET_COL_ADDR                  = const(0x15)
CMD_SET_ROW_ADDR                  = const(0x75)
CMD_SET_CONTRAST_CTRL             = const(0x81)
CMD_SET_REMAP                     = const(0xA0)
CMD_SET_DISP_START_LINE           = const(0xA1)
CMD_SET_DISP_OFFSET               = const(0xA2)
CMD_SET_DISP_MODE_NORMAL          = const(0xA4)
CMD_SET_DISP_MODE_ALL_ON          = const(0xA5)
CMD_SET_DISP_MODE_ALL_OFF         = const(0xA6)
CMD_SET_DISP_MODE_INVERSE         = const(0xA7) 
CMD_SET_MUX_RATIO                 = const(0xA8)
CMD_FUNCTION_SELECT_A             = const(0xAB)
CMD_SET_DISP_OFF                  = const(0xAE)
CMD_SET_DISP_ON                   = const(0xAF)
CMD_SET_PHASE_LENGTH              = const(0xB1)
CMD_NOP                           = const(0xB2)
CMD_SET_FRNT_CLK_DIV_FREQ         = const(0xB3)
CMD_GPIO                          = const(0xB5)
CMD_SET_SEC_PRECHARGE_PER         = const(0xB6)
CMD_SET_GRAYSCALE_TABLE           = const(0xB8)
CMD_LINEAR_LUT                    = const(0xB9)
CMD_NOP_2                         = const(0xBB)
CMD_SET_PRECHARGE_VOLT            = const(0xBC)
CMD_SET_VCOMH                     = const(0xBE)
CMD_FUNCTION_SELECT_B             = const(0xD5)
CMD_SET_COMMAND_LOCK              = const(0xFD)
CMD_CONT_HORZ_SCROLL_SET_RIGHT    = const(0x26)
CMD_CONT_HORZ_SCROLL_SET_LEFT     = const(0x27)
CMD_DEACTIVATE_SCROLL             = const(0x2E)
CMD_ACTIVATE_SCROLL               = const(0x2F)

# registers
REG_CMD  = const(0x80)
REG_DATA = const(0x40)

class SSD1327:
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.buffer = bytearray(self.width * self.height // 2)
        self.framebuf = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.GS4_HMSB)
        self.poweron()
        self.init_display()

    def init_display(self):
        for cmd in (
            CMD_SET_DISP_OFF,                 # Display OFF
            CMD_SET_COL_ADDR, 0x00, 0x7F,     # set column address (0, 127)
            CMD_SET_ROW_ADDR, 0x00, 0x7F,     # set row address (0, 127)
            CMD_SET_CONTRAST_CTRL, 0x80,      # set contrast control
            CMD_SET_REMAP, 0x51,              # remap memory, odd even columns, com flip and column swap
            CMD_SET_DISP_START_LINE, 0x00,    # Display start line is 0
            CMD_SET_DISP_OFFSET, 0x00,        # Display offset is 0
            CMD_SET_DISP_MODE_NORMAL,         # Normal display
            CMD_SET_MUX_RATIO, 0x7F,          # Mux ratio is 1/64
            CMD_SET_PHASE_LENGTH, 0x11,       # Set phase length
            #CMD_LINEAR_LUT,                  # Default gray scale table
            CMD_SET_GRAYSCALE_TABLE, 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x10,0x18,0x20,0x2F,0x38,0x3F,  # Set graytable
            CMD_SET_FRNT_CLK_DIV_FREQ, 0x50,  # Set dclk to 80Hz:0xC1 90Hz:0xE1   100Hz:0x00   110Hz:0x30 120Hz:0x50   130Hz:0x70
            CMD_FUNCTION_SELECT_A, 0x01,      # enable internal regulator
            CMD_SET_SEC_PRECHARGE_PER, 0x04,  # Set second pre-charge period
            CMD_SET_VCOMH, 0x0F,              # Set vcom voltage
            CMD_SET_PRECHARGE_VOLT, 0x08,     # Set pre-charge voltage
            CMD_FUNCTION_SELECT_B, 0x62,      # function selection B
            CMD_SET_COMMAND_LOCK, 0x12,       # command unlock
            CMD_SET_DISP_ON                   # Display ON
            ):
            print(cmd)  # Debug configuration
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def poweroff(self):
        self.write_cmd(CMD_FUNCTION_SELECT_A)
        self.write_cmd(0x00) # Disable internal VDD regulator, to save power
        self.write_cmd(CMD_SET_DISP_OFF)

    def poweron(self):
        self.write_cmd(CMD_FUNCTION_SELECT_A)
        self.write_cmd(0x01) # Enable internal VDD regulator
        self.write_cmd(CMD_SET_DISP_ON)

    def contrast(self, contrast):
        self.write_cmd(CMD_SET_CONTRAST_CTRL)
        self.write_cmd(contrast) # 0-255

    def invert(self, invert):
        self.write_cmd(CMD_SET_DISP_MODE_INVERSE if invert else CMD_SET_DISP_MODE_NORMAL)

    def show(self):
        self.write_cmd(CMD_SET_COL_ADDR)
        self.write_cmd((128 - self.width) // 4)
        self.write_cmd(63 - ((128 - self.width) // 4))
        self.write_cmd(CMD_SET_ROW_ADDR)
        self.write_cmd(0x00)
        self.write_cmd(self.height - 1)
        self.write_data(self.buffer)

    def fill(self, col):
        self.framebuf.fill(col)

    def pixel(self, x, y, col):
        self.framebuf.pixel(x, y, col)

    def scroll(self, dx, dy):
        self.framebuf.scroll(dx, dy)
        # software scroll

    def text(self, string, x, y, col=15):
        self.framebuf.text(string, x, y, col)
        
    def blit(self, fbuf, x, y, trans):
        self.framebuf.blit(fbuf, x, y, trans)


class SSD1327_I2C(SSD1327):
    def __init__(self, width, height, i2c, addr=0x3c, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.temp[0] = REG_CMD # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        self.temp[0] = self.addr << 1
        self.temp[1] = REG_DATA # Co=0, D/C#=1
        self.i2c.start()
        self.i2c.write(self.temp)
        self.i2c.write(buf)
        self.i2c.stop()
        
class SSD1327_SPI(SSD1327):
    def __init__(self, width, height, spi, dc, res, cs, external_vcc=False):
        self.rate = 10000000
        dc.init(dc.OUT, value=0)
        res.init(res.OUT, value=1)
        cs.init(cs.OUT, value=1)
        print(dc, res, cs)
        self.spi = spi
        self.dc = dc
        self.res = res
        self.cs = cs
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs.value(True)
        self.dc.value(False)
        self.cs.value(False)
        self.spi.write(bytearray([cmd]))
        self.cs.value(True)

    def write_data(self, buf):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs.value(True)
        self.dc.value(True)
        self.cs.value(False)
        self.spi.write(buf)
        self.cs.value(True)