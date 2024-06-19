import os
import base64
import requests
import threading
import io
import imghdr

import json
import logging
from PIL import Image

lock = threading.Lock()
# 配置日志记录器
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def image_to_base64(image_path):
    try:
        with Image.open(image_path) as image:
            # Determine image MIME type
            mime_type = imghdr.what(image.filename)

            if mime_type is None:
                logging.error(f"Invalid image file: {image_path}")
                return ""

            # Convert image to RGB if it's in a different mode
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Convert image to JPEG and save in a bytes buffer
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG")
            image_data = buffer.getvalue()

            # Encode the image data
            encoded_string = base64.b64encode(image_data).decode("utf-8")

            # Return the data URL for a JPEG
            return f"data:image/jpeg;base64,{encoded_string}"

    except FileNotFoundError:
        logging.error(f"File not found: {image_path}")
        return ""


def send_image_to_api(base64_image: str) -> str:
    data = {
        "model": "llava-step-v1-vision",
        "stream": False,
        "messages": [
            {
                "content": [
                    {
                        "text": "描述一下这张表情包的内容",
                        "type": "text"
                    },
                    {
                        "image_url": {
                            "detail": "auto",
                            "url": "{MyBase64Pic}"
                        },
                        "type": "image_url"
                    }
                ],
                "role": "user"
            }
        ]
    }
    data["messages"][0]["content"][1]["image_url"]["url"] = base64_image

    # 构建请求体
    request_body = json.dumps(data)

    # 发送POST请求
    url = "your_url"
    try:
        token = "your_token"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        response = requests.post(url, data=request_body, headers=headers)
        response.raise_for_status()  # 检查响应状态
        # 将响应文本转换为Python的字典对象
        response_dict = json.loads(response.text)
        # 提取 "content" 键的值
        content_text = response_dict['choices'][0]['message']['content']
        logging.info(content_text)
        return content_text
    except requests.exceptions.RequestException as e:
        logging.info(f"Error sending image to API: {e}")
        return ""


def process_image(image_path: str, json_file: str) -> None:
    base64_image = image_to_base64(image_path)
    response_text = send_image_to_api(base64_image)

    if base64_image and response_text:
        data_to_write = {
            'filename': image_path,
            'content': response_text
        }
        # 转为JSON字符串
        with open(json_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data_to_write, ensure_ascii=False))  # 确保直接写入非 ASCII 字符
            f.write(',')
            f.write('\n')  # 换行
        try:
            os.remove(image_path)
        except OSError as e:
            logging.info(f"Error removing image file {image_path}: {e}")
    #获取失败
    else:
        logging.info("No image or response text found.")
        # 报错后重新再进入一次process_image
        process_image(image_path, json_file)


def main():
    image_folder = "./Pictures"
    json_file = os.path.join("./", 'response_data.json')  # 在图像文件夹创建一个文本文件
    # 如果文件不存在，则创建一个新文件，并写入一个"["和\n
    if not os.path.exists(json_file):
        with open(json_file, 'w', encoding='utf-8') as f:
            f.write('[')
            f.write('\n')
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
        # 对内容进行处理
        if content.endswith(']'):
            content = content[:-1]
            content = content.rstrip() + ','
            # 将处理后的内容写回文件
    with open(json_file, 'w', encoding='utf-8') as f:
        f.write(content)
    # 获取所有图像文件
    image_files = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if
                   os.path.isfile(os.path.join(image_folder, f))]

    # 当图片文件列表不为空时，循环处理每一张图片
    while image_files:
        image_file = image_files.pop()
        process_image(image_file, json_file)  # 给 process_image 传递文本文件的路径
        # 更新图片文件列表（以处理可能在循环执行过程中新增的图片文件）
        image_files = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if
                       os.path.isfile(os.path.join(image_folder, f))]

    # 读取文件内容
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 对内容进行处理
    if content.endswith(',\n'):
        content = content[:-2] + '\n'  # 删除最后的 ",\n"
    if not content.endswith(']'):
        content = content.rstrip() + '\n'
        content = content.rstrip() + ']'  # 在去掉尾部空白后，追加 "]"

    # 将处理后的内容写回文件
    with open(json_file, 'w', encoding='utf-8') as f:
        f.write(content)

    # 使用日志记录器记录消息
    logging.info(f"Response data saved to {json_file}")


if __name__ == "__main__":
    main()
