import json
import logging
import math
import os
import time

import pandas as pd

log_level_dict = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}
# 配置日志记录器
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

json_file = "./01_data/01_bqb.json"
folder_path = "./01_data/01_bqb"


def retain_files_in_folder(json_file, folder_path):
    # 读取json文件
    with open(json_file, 'r', encoding='utf-8') as f:
        json_list = json.load(f)

    # 获取json中的文件名列表
    json_filenames = [item['filename'] for item in json_list]

    # 获取文件夹中所有的文件名称
    folder_files = os.listdir(folder_path)
    total_files = len(folder_files)

    delete_count = 0
    # 遍历文件夹中的文件
    for file in folder_files:
        # 构造文件路径
        file_path = os.path.join(folder_path, file)

        # 如果文件夹中的文件没有在json的文件列表中，删除该文件
        if file not in json_filenames and os.path.isfile(file_path):
            os.remove(file_path)
            delete_count += 1
            logging.info(f'Deleted file: {file_path}')

    return total_files, delete_count

# 用于删除表情包
if __name__ == '__main__':
    firstTime = time.time()
    logging.info('-------------------------------------------')
    logging.info('原神表情包检查批处理操作启动！')
    logging.info(f'表情包的json文集名: {json_file}')
    logging.info(f'删除文件的路径: {folder_path}')
    logging.info('-------------------------------------------\n')

    total_images, successful_count = retain_files_in_folder(json_file, folder_path)
    
    lastTime = time.time()
    time_taken_seconds = lastTime - firstTime
    hours, remainder = divmod(time_taken_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # 使用日志记录器记录消息
    logging.info('\n-------------------------------------------')
    logging.info(f"总共处理了：{total_images}张表情包")
    logging.info(f"成功删除处理：{successful_count}张表情包")
    logging.info(f"剩余表情包：{total_images - successful_count:.1f}张")
    logging.info(f"总共花费时间：{hours:.1f}小时, {minutes:.1f}分钟, {seconds:.1f}秒.")
    logging.info('-------------------------------------------')
