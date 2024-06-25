import json
import os
import random
import string
import logging
from typing import Tuple

class adminService():
    def __init__(self):
        # 存储的管理员及激活码
        self.admin_id = []
        self.admin_password = []
        # 读取配置文件
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            self.admin_id = config["admin_id"]
            self.admin_password = config["admin_password"]
            if self.admin_password == "":
                # 生成随机密码
                self.admin_password = ''.join(random.sample(string.ascii_letters + string.digits, 8))
            print(f"[adminService] 读取配置文件成功! admin_id: {self.admin_id}, admin_password: {self.admin_password}")

    # 认证管理员,然后写入config中
    def verify_admin(self, user_id: str, admin_password: str) -> bool:
        if admin_password != self.admin_password:
            return False
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        self.admin_id.append(user_id)
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            config["admin_id"].append(user_id)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        return True
        

    def is_admin(self, user_id: str) -> bool:
        return user_id in self.admin_id

    # 修改管理员密码
    def update_password(self, user_id: str, admin_password: str) -> bool:
        if self.is_admin(user_id) == False:
            print("False!")
            return False
        self.admin_password = admin_password
        # 保存配置文件, 修改配置文件为新密码
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            config["admin_password"] = admin_password
            print(admin_password)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        print(f"[adminService] 修改管理员密码成功! admin_password: {self.admin_password}")
        return True

    # 修改插件中的host
    def change_host(self, user_id: str, host: str) -> bool:
        if self.is_admin(user_id) == False:
            return False
        # 保存配置文件, 修改配置文件为新host
        # 将修改后的host写入文件,插件应该在上一文件夹,其他之不需要修改
        config_path = os.path.join(os.path.dirname(__file__), "../config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            config["start"]["host"] = host
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        print(f"[adminService] 修改host成功! host: {host}")
        return True

    # 修改插件中的port
    def change_port(self, user_id: str, port: int) -> bool:
        if self.is_admin(user_id) == False:
            return False
        config_path = os.path.join(os.path.dirname(__file__), "../config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            config["start"]["port"] = port
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        print(f"[adminService] 修改port成功! port: {port}")
        return True

    # 清空现有的管理员名单
    def clear_admin(self, user_id: str) -> bool:
        if self.is_admin(user_id) == False:
            return False
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            config["admin_id"] = []
            config["admin_id"].append(user_id)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        print(f"[adminService] 清空管理员成功!")
        return True
