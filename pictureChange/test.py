from adminService.adminService import adminService

# 调用模块中的函数，初始化他的类
ad = adminService()

# 调用模块中的函数，执行他的类的方法
print(ad)
print(ad.verify_admin('admin', 'admin'))
ad.update_json("root", "use_pictureChange", value="True")
ad.update_json("root", "start", "port", value="7777")
ad.update_json("root", "defaults", "params", "sampler_name", value="Euler r")
