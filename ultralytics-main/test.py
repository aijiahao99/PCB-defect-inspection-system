import unittest
import sql

# 该文件用于进行系统功能的自动化测试
# 状态 - 未完成
# * 运行前修改测试参数
# C:\Users\Bao\Desktop\PythonProject3\ultralytics-main\sql.py
# C:\Users\Bao\Desktop\PythonProject3\ultralytics-main\test.py
# 数据库模块测试
class Database_test(unittest.TestCase):

    def __init__instance(self):

        self.case = sql.Sql_connect()
        return True

    # 测试数据库是否连接成功
    def test_sqlconnect(self):
        self.case = sql.Sql_connect()



    # 测试正则表达式函数模块
    def test_register_valid(self):
        # 成功测试
        self.assertTrue(self.case.if_register_valid("root","Test@123","example123@gmail.com"))
        # 失败测试
        self.assertFalse(self.case.if_register_valid("123","123445","qwe123"))

    # 测试数据库操作
    def test_database_operations(self):
        # 登入成功测试
        self.assertTrue(self.case.user_login("123","root"))
        # 登入失败测试
        self.assertFalse(self.case.user_login("123", "123"))
        # 注册成功测试
        self.assertTrue(self.case.user_register("root","Test@123","example123@gmail.com","user"))
        # 注册失败测试 （可引用以上测试例）
        self.test_register_valid()
        # pcb删除成功测试
        #self.assertTrue(self.case.pcb_delete('I0FDM-E55LL-TCVII-J9XT9'))
        # pcb删除失败测试
        self.assertFalse(self.case.pcb_delete("123"))
        # 用户账号删除成功测试
        self.assertTrue(self.case.user_delete("root","Test@123"))
        # 用户账号删除失败测试
        self.assertFalse(self.case.user_delete("123","test"))
        # 用户反馈测试
        self.assertTrue(self.case.user_feedback("root","very good"))

    # 测试账号信息修改
    def test_user_account_modification(self):
        # 测试成功测试
        self.assertTrue(self.case.update_user_password("123","123"))

    # 测试检测结果的数据库操作
    def test_identification_storage(self):
        self.case = detect.model_predict()
        self.case.run_model()



if __name__ == '__main__':
    unittest.main()
