import concurrent.futures
import json
import logging
import os
import threading
import time

import pandas as pd
import requests

log_level_dict = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

lock = threading.Lock()

file_name = "Ywen_data/Ywen_bqb.json"
data_xlsx = "./Ywen_bqb.xlsx"
n = 300

# 配置日志记录器
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def check_url(data):
    tem_valid_data = []
    tem_successful_count = 0
    failed_count = 0
    tem_data_count = len(data)
    thread_name = threading.current_thread().getName()
    logging.info(f"进程{thread_name} 开始检查表情包......")
    # 检查url有效性并保存有效数据
    for item in data:
        url = item['filename']
        try:
            # response = requests.head(url)
            # if response.status_code == 200:
            # with lock:
            #     tem_valid_data.append(item)
            if True:
                tem_valid_data.append(item)
                tem_successful_count += 1
                remaining_images = tem_data_count - tem_successful_count - failed_count
                logging.info(f"进程{thread_name} 表情包检查成功: {url}，还剩余{remaining_images}张图片未处理")
            else:
                failed_count += 1
                remaining_images = tem_data_count - tem_successful_count - failed_count
                logging.info(
                    f"进程{thread_name} 表情包检查失败: {url}，还剩余{remaining_images}张图片未处理")

        except requests.exceptions.RequestException as e:
            failed_count += 1
            remaining_images = tem_data_count - tem_successful_count - failed_count
            logging.info(
                f"进程{thread_name} 表情包检查失败: {url}，还剩余{remaining_images}张图片未处理")

    return tem_valid_data


def split(data, n):
    size = len(data) // n
    if len(data) % n:
        size += 1
    splits = [data[i:i + size] for i in range(0, len(data), size)]
    return splits


#  用于检查表情包
if __name__ == '__main__':
    firstTime = time.time()
    logging.info('-------------------------------------------')
    logging.info(f'检查表情包数据开启线程: {n}')
    logging.info('原神表情包检查批处理操作启动！')
    logging.info(f'检查数据的xlsx文件名: {data_xlsx}')
    # logging.info(f'上传表情包结果存储文件名: {file_name}')
    logging.info('-------------------------------------------\n')

    # 用于检查xlsx文件
    # df = pd.read_excel(file_name, engine='openpyxl')
    # json_list = []
    # for index, row in df.iterrows():
    #     row_dict = {}
    #
    #     # 遍历每一列
    #     for column in df.columns:
    #         # 如果列名是"url"或"description"
    #         if column == "url" or column == "description":
    #             row_dict[column] = row[column]
    #
    #     # 将非空行的数据添加到 json_list
    #     json_list.append(row_dict)
    # all_count = len(json_list)
    # logging.info(f"本次一共要处理：{all_count}张表情包")
    #
    # # 去除 'url' 和 'description' 列的空值
    # df = df.dropna(subset=['url', 'description'])
    # json_list = []
    # # 遍历每一行
    # for index, row in df.iterrows():
    #     row_dict = {}
    #
    #     # 遍历每一列
    #     for column in df.columns:
    #         # 如果列名是"url"或"description"
    #         if column == "url" or column == "description":
    #             row_dict[column] = row[column]
    #
    #     # 将非空行的数据添加到 json_list
    #     json_list.append(row_dict)

    json_file = os.path.join("./", file_name)
    # 读取json文件
    with open(json_file, 'r', encoding='utf-8') as f:
        json_list = json.load(f)
    all_count = len(json_list)

    logging.info(f"本次要处理有效表情包：{len(json_list)}张表情包, 无效表情包：{all_count - len(json_list)}张")
    time.sleep(1)
    splits = split(json_list, n)
    with concurrent.futures.ThreadPoolExecutor(max_workers=n) as executor:
        results = list(executor.map(check_url, splits))
    # results 是一个二维列表，将其拼接成一维列表
    valid_data = [item for sublist in results for item in sublist]

    # 将验证通过的URL保存到 Excel
    df = pd.DataFrame(valid_data)
    df.to_excel(data_xlsx, index=False)

    lastTime = time.time()
    time_taken_seconds = lastTime - firstTime
    hours, remainder = divmod(time_taken_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    successful_count = len(valid_data)
    data_count = len(json_list)
    logging.info('\n-------------------------------------------')
    logging.info(f"将响应数据保存到了：{data_xlsx}")
    logging.info(f"总共处理了：{data_count}张表情包")
    logging.info(f"成功处理：{successful_count}张表情包")
    logging.info(f"无效表情包：{all_count - data_count + successful_count:.1f}张")
    logging.info(f"总共花费时间：{hours:.1f}小时, {minutes:.1f}分钟, {seconds:.1f}秒.")
    logging.info('-------------------------------------------')
