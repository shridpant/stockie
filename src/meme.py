from PIL import Image, ImageDraw, ImageFont
import os

# INPUT
im = Image.open('C:/Users/User/Documents/GitHub/stockie/static/readme/screenshot.png')
top = "Hello\nOkayayayayayaya"

# CONFIGURATION
width, height = im.size
arial = ImageFont.truetype("arial.ttf", size=80)
draw = ImageDraw.Draw(im)
t_width, t_height = draw.multiline_textsize(top, font=arial)
print(width, height)
print(t_width, t_height)

# TOP
draw.multiline_text(((width-t_width)/2,(0)), top, font=arial, fill="black")


im.save("hello.png", "PNG")