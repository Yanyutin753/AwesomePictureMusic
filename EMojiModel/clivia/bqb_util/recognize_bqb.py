import base64
import concurrent
import concurrent.futures
import imghdr
import io
import json
import logging
import os
import threading
import time
from typing import Tuple

import requests
from PIL import Image

# 配置日志记录器
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# # 请求live地址
# request_liveUrl = "http://localhost:8000/token/check"
# 请求chat地址
request_url = ""
# 请求密钥
request_apikey = []
# 重试次数
request_tries = 1
# 重试时间间隔
request_delay = 1
# 表情包文件夹路径
image_folder = "./bqb_pic2"
# json文件名
json_name = "response_data_2.json"
# 请求token文件夹
token_file = "token.txt"
#  开启线程锁
lock = threading.Lock()
index = 0


def initializeToken():
    global request_apikey
    with open(token_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.strip() != '':
                request_apikey.append(line.strip())

            #  由于检查token是否有效
            # data = {
            #     "token": line.strip(),
            # }
            # response = requests.post(request_liveUrl, data=data)
            # response.raise_for_status()  # 检查响应状态
            #
            # content_text = response.json().get('live', None)
            # if content_text:
            #     logging.info(f"有效的API密钥: {line.strip()}")
            #     request_apikey.append(line.strip())
            # else:
            #     logging.info(response.text)
            #     logging.error(f"无效的API密钥: {line.strip()}")


def image_to_base64(image_path):
    try:
        with Image.open(image_path) as image:
            # Determine image MIME type
            mime_type = imghdr.what(image.filename)

            if mime_type is None:
                logging.error(f"不合法的文件: {image_path}")
                return None

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
        logging.error(f"文件不存在: {image_path}")
        return None


def send_image_to_api(base64_image: str, image_path: str, thread_num):
    data = {
        "model": "yi-vl-plus",
        "stream": False,
        "messages": [
            {
                "content": [
                    {
                        "text": "分析这张表情包的内容，表情含义，以及在特定文化或网络上下文中的使用和理解，进行总结成一大段话告诉我",
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
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {request_apikey[thread_num]}"
        }
        response = requests.post(request_url, data=request_body, headers=headers)
        response.raise_for_status()  # 检查响应状态
        # 将响应文本转换为Python的字典对象
        response_dict = json.loads(response.text)
        # 提取 "content" 键的值
        content_text = response_dict['choices'][0]['message']['content']
        return content_text

    except Exception as e:
        logging.info(f"线程{thread_num}请求返回状态码: {response.status_code} 信息: {response.text}")
        logging.error(f"分析{image_path}发生错误: {e}")
        return None


def process_image(image_path: str, json_file: str, thread_num) -> Tuple[bool, bool]:
    try:
        base64_image = image_to_base64(image_path)
        response_text = send_image_to_api(base64_image, image_path, thread_num)

        for i in range(request_tries):
            if response_text is not None:
                break
            else:
                logging.info(f"线程{thread_num}尝试第{i + 1}次重新上传{image_path}...... ")
                time.sleep(request_delay)
                response_text = send_image_to_api(base64_image, image_path, thread_num)

        if base64_image or response_text:
            if response_text is None or response_text == "":
                logging.error(f"表情包不合格: {image_path}，已跳过处理！")
                return True, False
            data_to_write = {
                'filename': os.path.basename(image_path),
                'content': response_text
            }
            # 加锁处理
            with lock:
                with open(json_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(data_to_write, ensure_ascii=False, indent=4))
                    f.write(',')
                    f.write('\n')
            try:
                os.remove(image_path)
                return True, True
            except OSError as e:
                logging.error(f"删除{image_path}发生错误: {e}")
                return False, False
        else:
            logging.error(f"删除失败: {image_path}")
            return False, False

    except OSError as e:
        logging.error(f"删除{image_path}失败: {e}")
        return False, False


def get_thread_num(thread_name):
    thread_num = int(thread_name.split('_')[1])
    return thread_num


# 处理图像任务
def process_image_task(image_files_subset):
    successful_count = 0
    failed_count = 0
    thread_name = threading.current_thread().getName()
    thread_num = get_thread_num(thread_name)
    logging.info(f"进程{thread_num}，请求密钥: {request_apikey[thread_num][-10:]}，开始处理表情包......")
    # 获取线程编号

    for image_file in image_files_subset:
        result, success = process_image(image_file, json_name, thread_num)
        if result and success:
            successful_count += 1
            remaining_images = len(image_files_subset) - successful_count - failed_count
            logging.info(f"进程{thread_num} 成功分析表情包: {image_file}，还剩余{remaining_images}张图片未处理")
        else:
            failed_count += 1
            remaining_images = len(image_files_subset) - successful_count - failed_count
            logging.info(
                f"进程{thread_num} 失败分析表情包: {image_file}，还剩余{remaining_images}张图片未处理")
    return successful_count


# 分割文件列表
def divide_list(lst, n):
    k, m = divmod(len(lst), n)
    return (lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


def main():
    n = len(request_apikey)
    json_file = os.path.join("./", json_name)
    firstTime = time.time()

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

    total_images = len(image_files)
    logging.info("本次要处理的图片数量: %d", total_images)
    image_files_subset = list(divide_list(image_files, n))

    with concurrent.futures.ThreadPoolExecutor(max_workers=n) as executor:
        # 使用map处理所有图像
        results = executor.map(process_image_task, image_files_subset)

    successful_count = sum(results)

    # 读取文件内容
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 对内容进行处理
    if content.endswith(',\n'):
        # 删除最后的 ",\n"
        content = content[:-2] + '\n'
    if not content.endswith(']'):
        content = content.rstrip() + '\n'
        # 在去掉尾部空白后，追加 "]"
        content = content.rstrip() + ']'

    with open(json_file, 'w', encoding='utf-8') as f:
        f.write(content)

    lastTime = time.time()
    time_taken_seconds = lastTime - firstTime
    hours, remainder = divmod(time_taken_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # 使用日志记录器记录消息
    logging.info('\n')
    logging.info('-------------------------------------------')
    logging.info(f"将响应数据保存到了：{json_file}")
    logging.info(f"总共处理了：{total_images}张表情包")
    logging.info(f"成功处理：{successful_count}张表情包")
    logging.info(f"无效表情包：{total_images - successful_count:.1f}张")
    logging.info(f"总共花费时间：{hours:.1f}小时, {minutes:.1f}分钟, {seconds:.1f}秒.")
    logging.info('-------------------------------------------')


#  用于分析表情包
if __name__ == "__main__":
    logging.info('-------------------------------------------')
    logging.info('原神表情包识别批处理操作启动！')
    initializeToken()
    n = len(request_apikey)
    logging.info(f'请求地址: {request_url}')
    logging.info(f"已加载{n}个API密钥")
    logging.info(f'请求 API 密钥已设定: {request_apikey}')
    logging.info(f'重试次数设定为: {request_tries} 次')
    logging.info(f'每次重试之间的延迟设定为: {request_delay} 秒')
    logging.info(f'表情包文件夹路径设定为: {image_folder}')
    logging.info(f'分析表情包数据存储文件名: {json_name}')
    logging.info(f'分析表情包数据开启线程: {n}')
    logging.info('-------------------------------------------')
    logging.info('\n')
    image_files = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if
                   os.path.isfile(os.path.join(image_folder, f))]

    total_images = len(image_files)
    count = 0
    while total_images > 0:
        count += 1
        main()
        total_images = len([f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))])
        if total_images > 0:
            logging.info('\n')
            logging.info('\n')
            logging.info('-------------------------------------------')
            logging.info(f'开启第{count + 1}次分析表情包\n')


