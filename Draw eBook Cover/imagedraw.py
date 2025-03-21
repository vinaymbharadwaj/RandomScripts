from PIL import ImageFont, ImageDraw, Image
image = Image.new('RGB', (600, 800), color = (0, 0, 0))
draw = ImageDraw.Draw(image)

s = "Of a Linear Circle"
a = s.split()
message = ''
for i in range(0, len(a), 4):
    message += ' '.join(a[i:i+4]) + '\n'

font = ImageFont.truetype('trebuc.ttf', size=30)
bounding_box = [60, 80, 540, 720]
x1, y1, x2, y2 = bounding_box  
w, h = draw.textsize(message, font=font)
x = (x2 - x1 - w)/2 + x1
y = (y2 - y1 - h)/2 + y1
draw.text((x, y), message, align='center', font=font)
draw.rectangle([x1, y1, x2, y2])
image.show()
image.save('cover.jpg')