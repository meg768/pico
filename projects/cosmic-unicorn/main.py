import time
import machine

from cosmic import CosmicUnicorn
from picographics import PicoGraphics, DISPLAY_COSMIC_UNICORN as DISPLAY
from pngdec import PNG

# overclock to 200Mhz
machine.freq(200000000)


# create cosmic object and graphics surface for drawing
cosmic = CosmicUnicorn()
graphics = PicoGraphics(DISPLAY)


graphics.clear()
cosmic.set_brightness(0.9)

png = PNG(graphics)
png.open_file("32x32.png")

width = png.get_width()
print(width)

index = 32

BLACK = graphics.create_pen(0, 0, 0)

while index > 0:
    graphics.set_pen(BLACK)
    graphics.clear()
    png.decode(index, 0 ,source = (0, 0, 32, 32))
    cosmic.update(graphics)
    index = index - 1


while index <= width:

    graphics.set_pen(BLACK)
    graphics.clear()
    png.decode(0, 0 ,source = (index, 0, 32, 32))
    cosmic.update(graphics)
    index = index + 1



