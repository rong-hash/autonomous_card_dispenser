import base64
from PIL import Image
import io

def image_to_base64(image_path):
    # 打开图片文件
    with Image.open(image_path) as image:
        # 将图片转换为二进制数据
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_data = buffered.getvalue()

        # 将二进制数据编码为Base64字符串
        img_base64 = base64.b64encode(img_data)
        
        # Python 3.x需要解码成字符串
        return img_base64.decode('utf-8')


def binary2base64(image_binary):
    img_base64 = base64.b64encode(image_binary)
    return img_base64.decode('utf-8')