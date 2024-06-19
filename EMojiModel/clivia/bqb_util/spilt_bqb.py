import logging
import math
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


data_xlsx = "./data/Ywen_bqb.xlsx"
partitions = 5


def split_excel_file(dataXlsx, num_files):
    df = pd.read_excel(dataXlsx, engine='openpyxl')

    # 总行数除以文件数目确定每个文件包含的行数
    rows_per_file = math.ceil(len(df) / num_files)

    for i in range(num_files):
        start = i * rows_per_file
        end = (i + 1) * rows_per_file if (i + 1) * rows_per_file < len(df) else len(df)
        split_df = df.iloc[start:end]
        split_df.to_excel(f'bqb_{i + 1}.xlsx', index=False)
        logging.info(f'分割文件 {i + 1} 完成！')


# 用于分割表情包
if __name__ == '__main__':
    firstTime = time.time()
    logging.info('-------------------------------------------')
    logging.info('原神表情包检查批处理操作启动！')
    logging.info(f'分割xlsx的个数: {partitions}')
    logging.info(f'检查数据的xlsx文件名: {data_xlsx}')
    logging.info('-------------------------------------------\n')
    split_excel_file(data_xlsx, partitions)
