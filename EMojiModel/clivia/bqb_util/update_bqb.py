import concurrent.futures
import json
import logging
import os
import threading
import time

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

# 表情包文件夹路径
image_folder = "./bqb_pic2/"

# 结果json文件名
res_json_name = "res_2.json"

# 原始json
json_name = "response_data_2.json"

# 请求地址
request_url = 'https://chatglm.cn/chatglm/backend-api/assistant/file_upload'

data_xlsx = "./bqb_res_3.xlsx"

# 请求ChatGlm密钥
request_apikey = []

# 请求线程
n = 10

# 重试次数
request_tries = 1
# 重试时间间隔
request_delay = 1

log_level_dict = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)

logger = logging.getLogger()
logger.addHandler(stream_handler)
logger.setLevel(log_level_dict.get("INFO", logging.DEBUG))

# accessTokenRequestQueueMap = defaultdict(list)

#  开启线程锁
lock = threading.Lock()

index = 0


def getToken():
    global index
    with lock:
        if not request_apikey:
            return None
        else:
            index += 1
            return request_apikey[index % len(request_apikey)]


# def requestToken(refreshToken):
#     if accessTokenRequestQueueMap[refreshToken]:
#         logger.info('Refresh failed')
#         return accessTokenRequestQueueMap[refreshToken].pop(0)
#
#     try:
#         response = requests.post(
#             "https://chatglm.cn/chatglm/backend-api/v1/user/refresh",
#             headers={
#                 "Authorization": f"Bearer {refreshToken}",
#                 "Referer": "https://chatglm.cn/main/alltoolsdetail",
#                 "X-Device-Id": uuid4().hex,
#                 "X-Request-Id": uuid4().hex,
#                 "Accept": "*/*",
#                 "App-Name": "chatglm",
#                 "Platform": "pc",
#                 "Origin": "https://chatglm.cn",
#                 "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
#                 "Sec-Ch-Ua-Mobile": "?0",
#                 "Sec-Ch-Ua-Platform": '"Windows"',
#                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
#                               "Chrome/122.0.0.0 Safari/537.36",
#                 "Version": "0.0.1",
#             },
#         )
#         logger.info(response.text)
#     except Exception as e:
#         logger.info(e)
#         accessTokenRequestQueueMap[refreshToken].append(e)

def check_url(file_url):
    try:
        response = requests.get(file_url)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        return False


def update_file(dataJson):
    thread_name = threading.current_thread().getName()
    logging.info(f"进程{thread_name} 开始上传表情包......")
    successful_count = 0
    failed_count = 0
    tem_valid_data = []
    # 建立头部信息
    token = getToken()
    logging.info(f"进程{thread_name}请求API密钥: {token}")
    headers = {'Authorization': f'Bearer {token}'}
    tem_data_count = len(dataJson)
    # 创建一个Session，并配置重试策略
    session = requests.Session()
    retries = Retry(total=request_tries, backoff_factor=request_delay, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    for dictionary in dataJson:
        # 获取图片文件列表
        filePath = image_folder + dictionary.get('filename')
        if not os.path.exists(filePath):
            failed_count += 1
            remaining_images = tem_data_count - successful_count - failed_count
            logging.error(f"进程{thread_name}表情包不存在: {filePath}，还剩余{remaining_images}张表情包未处理")
            continue
        with open(filePath, 'rb') as f:
            files = {'file': f}
            response = session.post(request_url, headers=headers, files=files)
            logging.info(
                f"进程{thread_name}请求返回状态码: {response.status_code} 信息: {response.json().get('message')}")

        if response.status_code == 200 and response.json().get('message') == "success":
            successful_count += 1
            remaining_images = tem_data_count - successful_count - failed_count
            file_url = response.json().get('result').get('file_url')
            if check_url(file_url):
                new_dict = {"filename": file_url, "content": dictionary['content']}
                # 添加新的字典到列表的尾部
                tem_valid_data.append(new_dict)
                try:
                    os.remove(filePath)
                    logging.info(f"进程{thread_name}成功上传表情包: {filePath}，还剩余{remaining_images}张表情包未处理")
                except OSError as e:
                    logging.error(
                        f"进程{thread_name}删除{filePath}发生错误: {e}，还剩余{remaining_images}张表情包未处理")
            else:
                failed_count += 1
                remaining_images = tem_data_count - successful_count - failed_count
                logging.error(f"进程{thread_name}失败上传表情包: {filePath}，还剩余{remaining_images}张表情包未处理")

        else:
            failed_count += 1
            remaining_images = tem_data_count - successful_count - failed_count
            logging.error(f"进程{thread_name}失败上传表情包: {filePath}，还剩余{remaining_images}张表情包未处理")

    return tem_valid_data


def split(data):
    size = len(data) // n
    if len(data) % n:
        size += 1
    return [data[i:i + size] for i in range(0, len(data), size)]

# 用于上传更新表情包
if __name__ == '__main__':
    firstTime = time.time()
    logging.info('-------------------------------------------')
    logging.info('原神表情包上传批处理操作启动！')
    logging.info(f'请求地址: {request_url}')
    logging.info(f'请求 API 密钥已设定: {request_apikey}')
    logging.info(f'重试次数设定为: {request_tries} 次')
    logging.info(f'每次重试之间的延迟设定为: {request_delay} 秒')
    logging.info(f'表情包文件夹路径设定为: {image_folder}')
    logging.info(f'表情包数据存储文件名: {json_name}')
    logging.info(f'上传表情包结果存储文件名: {res_json_name}')
    logging.info(f'上传表情包数据开启线程: {n}')
    logging.info('-------------------------------------------\n')

    json_file = os.path.join("./", json_name)
    # 读取json文件
    with open(json_file, 'r', encoding='utf-8') as f:
        json_list = json.load(f)

    # 剔除content为空的数据
    json_list = [item for item in json_list if item['content'] != ""]

    total_images = len(json_list)
    logging.info(f"本次一共要检查：{total_images}张表情包")
    splits = split(json_list)

    with concurrent.futures.ThreadPoolExecutor(max_workers=n) as executor:
        results = list(executor.map(update_file, splits))

    # results 是一个二维列表，将其拼接成一维列表
    valid_data = [item for sublist in results for item in sublist]

    with open(res_json_name, 'w', encoding='utf-8') as f:
        json.dump(valid_data, f, ensure_ascii=False, indent=4)

    df = pd.DataFrame(valid_data)
    df.to_excel(data_xlsx, index=False)

    lastTime = time.time()
    time_taken_seconds = lastTime - firstTime
    hours, remainder = divmod(time_taken_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    successful_count = len(valid_data)
    # 使用日志记录器记录消息
    logging.info('\n-------------------------------------------')
    logging.info(f"将响应数据保存到了：{res_json_name}")
    logging.info(f"将响应数据保存excel：{data_xlsx}")
    logging.info(f"总共处理了：{total_images}张表情包")
    logging.info(f"成功处理：{successful_count}张表情包")
    logging.info(f"无效表情包：{total_images - successful_count:.1f}张")
    logging.info(f"总共花费时间：{hours:.1f}小时, {minutes:.1f}分钟, {seconds:.1f}秒.")
    logging.info('-------------------------------------------')
