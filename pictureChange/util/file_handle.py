import base64
import json
import mimetypes
import os

from common.log import logger


# 读取配置文件
def get_config_path(json_path: str):
    cursor = os.path.dirname(__file__)
    return os.path.join(cursor, json_path)


# 读取配置文件
def update_config(config_path, user_id, append):
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    if append:
        config["use_group"].append(user_id)
    else:
        config["use_group"].remove(user_id)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


# 用于图片和文件转成base64
def file_toBase64(image_path: str):
    if os.path.isfile(image_path):
        try:
            with open(image_path, 'rb') as file:
                image_data = file.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
                # 获取文件的MIME类型
                mime_type, _ = mimetypes.guess_type(image_path)
                if mime_type is None:
                    mime_type = "application/octet-stream"  # 默认MIME类型
                base64_image = f"data:{mime_type};base64,{base64_image}"
                return base64_image
        except Exception as e:
            logger.error(f"读取文件时出错: {e}")
            return None
    else:
        logger.warning(f"文件不存在: {image_path}")
        return None


def delete_file(file_content):
    if os.path.isfile(file_content):
        os.remove(file_content)
        logger.info("文件已成功删除")
    else:
        logger.error("文件不存在")
