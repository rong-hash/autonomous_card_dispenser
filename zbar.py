from pyzbar.pyzbar import decode
from PIL import Image
img = Image.open('temp.bmp')
print(decode(img))

