from adminService.adminService import adminService

# 调用模块中的函数，初始化他的类
ad = adminService()

# 调用模块中的函数，执行他的类的方法
print(ad)
print(ad.verify_admin('admin', 'admin'))
