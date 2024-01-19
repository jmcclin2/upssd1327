# upssd1327
Micropython SSD1327 display driver.  
- Adapted from several popular/available drivers found online.  

## Usage
- SPI interface ```from ssd1327 import SSD1327_SPI```
- I2C interface ```from ssd1327 import SSD1327_I2C```

## Example of showing a logo splash screen on an OLED display utilizing the SPI bus
```
from ssd1327 import SSD1327_SPI
import framebuf
import logo_data

# Setup display on SPI bus
spi = SPI(0, sck=Pin(6), mosi=Pin(7))
dc = Pin(8)
res = Pin(9)
cs = Pin(5)

# Initialize SSD1327 OLED Display
ssd1327 = SSD1327_SPI(128, 128, spi, dc, res, cs)

# Fill a local framebuffer with logo splash screen
a = bytearray(logo_data.data())
fbuf = framebuf.FrameBuffer(a, 128, 128, framebuf.GS4_HMSB)

# Show logo splash screen
ssd1327.fill(0)
ssd1327.blit(fbuf, 0, 0, 0)
ssd1327.show()
```
## Creating images with 4-bit Color-depth

I used the excellent graphics program [Asperite](https://www.aseprite.org) to generate the 'logo_data' shown in the example above.

There are two keys to generating imagery for the ssd1327:
1. Create or import a 128x128 pixel image.
2. Use a 4-bit color palette.
3. Export the data in a compatible format.

Here are the steps I used with Aseprite:

1. Load a 4-bit color palette.  An example palette (4_bit_color_palette.aseprite) can be found in the /tools directory of this repository.

![Load color palette](/tools/aseprite_load_palette.png)

2. Install and use the Lua export script (4_bit_export.lua) found in the /tools directory.
	- To find the script install location, go to File->Scripts->Open Scripts Folder
	- Copy 4_bit_export.lua into this folder
	- Restart Aseprite (may be required)

3. Load or create your 128x128 pixel image in Asperite.

4. Export your image using the 4_bit_export.lua script; when prompted for 'select file' click on button and choose filename for exported Python data file.

![Load color palette](/tools/aseprite_export_with_script.png)