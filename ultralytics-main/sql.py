# 连接底层数据库对象文件
import ast
import calendar
from datetime import datetime

import imagehash
import random
import re
import string
from argon2 import PasswordHasher
import numpy
import pandas
import pymysql
import time
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as ns
# 导入库
class Sql_connect:
    # 初始化函数
    def __init__(self):
        # 测试连接
        # 运行前，替换相应的参数
        try:
            self.conn = pymysql.connect(
                host="127.0.0.1", # 主机地址
                user="root", # 用户名
                passwd="root", # 密码
                port=3306, # 端口
                db="user_data" # 数据库名称
            )
            print(self.conn)
        except Exception as error_infor:
            print("Database connection error")
            print(error_infor)
        # 存储验证后的用户账号信息，以便进行之后的用户账号操作
        self.username = None
        self.password = None
        self.position = None
        self.times = 0
        self.email = ""
        # 数据库用户表名
        self.table_name = "login_infor"
        # 数据库pcb表名
        self.pcb_table_name = "items"
        # 产品序列号
        self.product_code = None
        # 报告单号
        self.report_id = None
        # 密码hash
        self.pass_hash = PasswordHasher(
            time_cost=4,  # 迭代次数
            memory_cost=35535,  # 内存消耗
            parallelism=2  # 并行度
        )

    # 通过hash获取产品序列号
    def get_product_code_by_hash(self, img_hash):
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            get = "select query_id from items where img_hash = \'" + img_hash + "\';"
            cursor.execute(get)
            product_id = cursor.fetchall()[0][0]
            return product_id
        except Exception as e:
            print("Database exception: ", e)

    # 获取数据表数据
    def get_table_data(self, table_name):
        self.update_sql_connection_status()
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            search = "select * from " + table_name + ";"
            cursor.execute(search)
            result = cursor.fetchall()
            if len(result) != 0:
                return result[0]
            return False
        except Exception as e:
            print("Database exception: ", e)

    # 判断报告是否存在
    def if_report_exists(self, product_id):
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            search = "select * from reports where product_number = \'" + product_id + "\';"
            cursor.execute(search)
            if len(cursor.fetchall()) != 0:
                return True
            return False
        except Exception as e:
            print("Database exception: ", e)

    # 删除所有数据
    def delete_all_data(self, table_name):
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            delete = "delete from " + table_name + ";"
            cursor.execute(delete)
            self.conn.commit()
            return True
        except Exception as e:
            print("Database exception: ", e)
    # 更新报告
    def update_report(self, new_report_id, product_id):
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            update = "update reports set report_number = \'" + new_report_id + "\' where product_number = \'" + product_id + "\';"
            cursor.execute(update)
            self.conn.commit()

        except Exception as e:
            print("Database exception: ", e)
    # 判断产品是否存在
    def if_product_exists(self, product_hash):
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            search = "select * from items where img_hash = \'" + product_hash + "\';"
            cursor.execute(search)
            if len(cursor.fetchall()) != 0:
                return True
            return False
        except Exception as e:
            print("Database exception: ", e)

    # 更新重复的产品信息
    def update_product_by_hash(self, product_hash, input_address,output_address,name, result, error_count, error_infor, detect_time = ""):
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            detect_time = self.auto_generate_time()
            update = ("update items set items_name = \'" + name
                      + "\',items_result = \'" + result + "\',"
                      + "items_input_address = \'" + input_address
                      + "\',items_output_address = \'" + output_address + "\',"
                      + "items_errorcount = \"" + error_count + "\","
                      + "items_errorinfor = \"" + error_infor + "\",detect_time = \'"
                      + detect_time + "\' "
                      "where img_hash = \'" + product_hash + "\';")
            print(update)
            cursor.execute(update)
            self.conn.commit()
        except Exception as e:
            print("Database exception: ", e)

    # 用户名验证
    def if_username_valid(self, username):
        try:
            cursor = self.conn.cursor()
            check = "select * from login_infor where user_name = \'" + username + "\';"
            cursor.execute(check)
            result = cursor.fetchall()
            if len(result) == 0:
                return True
            else:
                return False

        except Exception as e:
            print("Database exception: ", e)

    # 邮箱验证
    def if_email_address_valid(self, address):
        try:
            cursor = self.conn.cursor()
            check = "select * from login_infor where email = \'" + address + "\';"
            cursor.execute(check)
            result = cursor.fetchall()
            if len(result) == 0:
                return True
            else:
                return False

        except Exception as e:
            print("Database exception: ", e)

    # 正则表达式验证用户注册信息
    def if_register_valid(self, username, password, email_address):
        try:
            # 密码长度至少为8个字符，包含至少一个大写字母，包含至少一个小写字母，包含至少一个数字，包含至少一个特殊字符
            # 用户名长度不大于15个字符
            password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$%^&+=!]).{8,}$'
            # 邮箱规范验证
            address_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            # 验证
            if re.match(password_pattern, password) is not None:
                if len(username) <= 15:
                    if re.match(address_pattern,email_address) is not None:
                        return "pass"   # 验证通过
                    return "100"    # 邮箱地址错误码
                return "150"    # 用户名错误码
            return "200"    # 密码错误码
        except Exception as e:
            print("Database exception: ", e)

    # 加密存储密码
    def crypt_password(self, raw_password):
        generate_hash = self.pass_hash.hash(raw_password)
        return generate_hash

    # 用户注册模块
    def user_register(self, input_user_name, input_pass_word, input_address, input_position):
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            # 如果注册信息验证通过， 执行更新
            status = self.if_register_valid(input_user_name, input_pass_word, input_address)
            if status == 'pass':
                input_pass_word = self.crypt_password(input_pass_word)
                # sql更新语句
                insert = ("insert into " + self.table_name
                          + "(user_name, pass_word, email, times, last_login, position)"
                          + "values(\"" + input_user_name + "\",\"" + input_pass_word + "\",\""
                          + input_address + "\",0,\"" + str(self.auto_generate_time()) +"\",\"" + input_position + "\")")
                # 执行插入语句并提交
                cursor.execute(insert)
                self.conn.commit()
                # 更新参数
                self.username = input_user_name
                self.password = input_pass_word
                self.position = input_position
                # 更新登入时间
                self.update_user_login_times()
                return "pass"
            elif status == '100':
                return "Incorrect email address format"
            elif status == '150':
                return "The length of the username must be less than or equal to 15 characters"
            elif status == '200':
                return "The password must be at least 8 characters long, containing at least one capital letter, at least one lowercase letter, at least one digit, and at least one special character"
        except Exception as e:
            print("Database exception: ",e)

    # 随机生成报告单号
    def auto_generate_report_id(self):
        timestamp = time.strftime("%Y%m%d%H%M%S")
        rand_num = random.randint(1000, 9999)
        return f"RP-{timestamp}-{rand_num}"

    # 随机生成序列号模块
    def auto_generate_code(self, groups = 4, chars_per = 5):
        serial = []
        for _ in range(groups):
            group = ''.join(random.choices(string.ascii_uppercase + string.digits, k=chars_per))
            serial.append(group)
        # 返回序列号
        return '-'.join(serial)
    # 生成时间
    def auto_generate_time(self):
        local_time = time.localtime()
        formatted = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
        return formatted

    # 删除选择的行数据
    def delete_row_table_data(self, table_name, row_name, row_id):
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            delete = "delete from " + table_name + " where " + row_name + " = " + row_id + ";"
            print(delete)
            # 执行并提交
            cursor.execute(delete)
            self.conn.commit()
            return True
        except Exception as e:
            print("Database exception: ",e)

    # 更新用户登录时间模块
    def update_user_login_times(self):
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            # sql更新语句
            statement = ("update " + self.table_name +
                         " set times = times + 1,last_login = \"" + str(self.auto_generate_time()) +
                         "\" where user_name = \""
                         + self.username + "\" and pass_word = \""
                         + self.password + "\";")

            # 执行并提交
            cursor.execute(statement)
            self.conn.commit()
        except Exception as e:
            print("Database exception: ",e)

    # 存储被识别后的图片信息
    def pcb_register(self, product_id ,input_name, input_address,output_address,input_result, input_errorcount, input_type, input_errorinfor):
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            # 产品序列号
            self.product_code = product_id

            # 读取图片信息
            with open(input_address, 'rb') as file:
                # 转换图片二进制
                img_data = file.read()
            # 获取图片感知hash
            img_hash = imagehash.phash(Image.open(input_address))
            # sql插入语句
            insert = (("insert into " + self.pcb_table_name
                      + "(query_id, items_name, items_input_address,items_output_address, items_result, items_errorcount, items_errorinfor, items_type, detect_time, img_data, img_hash)")
                      + "values(\"" + self.product_code + "\",\"" + input_name + "\",\"" + input_address
                      + "\",\"" + output_address + "\",\"" + input_result + "\",\"" + input_errorcount + "\",\"" + input_errorinfor
                      + "\",\"" + input_type + "\",\"" + self.auto_generate_time() + "\",%s,\'" + str(img_hash) + "\')")

            print(insert)
            # 执行并提交
            cursor.execute(insert, (img_data))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"error {e}")

    # 查找和删除指定序列号的pcb信息
    def pcb_delete(self, input_code_number):
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            # 确认该序列号信息存在
            search = "select * from " + self.pcb_table_name + " where query_id = \"" + input_code_number + "\""
            cursor.execute(search)
            if len(cursor.fetchall()) == 0:
                return False
            # sql删除语句
            delete = "delete from " + self.pcb_table_name + " where query_id = \"" + input_code_number + "\""
            # 执行并提交
            cursor.execute(delete)
            self.conn.commit()
            return True

        except Exception as e:
            print("Database exception: ",e)

    # 查找和删除用户账号
    def user_delete(self, test_user_name = "", test_pass_word = ""):
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            # 该两个变量为测试使用, 正常调用不传值
            if len(test_user_name) != 0 and len(test_pass_word) != 0:
                self.username = test_user_name
                self.password = test_pass_word

            # 确认用户账号是否存在
            search = ("select * from " + self.table_name + " where user_name = \""
                      + self.username + "\" and pass_word = \"" + self.password + "\"")

            cursor.execute(search)
            if len(cursor.fetchall()) == 0:
                return False

            # sql删除语句
            delete = ("delete from " + self.table_name
                      + " where user_name = \""
                      + self.username + "\" and pass_word = \"" + self.password + "\"")

            # 执行并提交
            cursor.execute(delete)
            self.conn.commit()
            return True

        except Exception as e:
            print("Database exception: ", e)

    # 用户反馈模块
    def user_feedback(self, name, infor):
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            insert = ("insert into feedback(name,feedback_infor,datetime) values(\""
            + name + "\",\"" + infor + "\",\"" + str(self.auto_generate_time()) + "\")")

            cursor.execute(insert)
            self.conn.commit()
            return True

        except Exception as e:
            print("Database exception: ", e)

    # 报告信息存储模块
    def report_register(self, report_id, product_id = ''):
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            # 报告单号
            self.report_id = report_id
            if product_id != '':
                self.product_code = product_id
            insert = ("insert into reports(report_number,product_number,download_time) values(\""
                      + self.report_id + "\",\"" + self.product_code + "\",\"" + self.auto_generate_time() + "\")")

            cursor.execute(insert)
            self.conn.commit()
            return True

        except Exception as e:
            print("Database exception: ", e)

    # 更新数据库连接，避免长时间使用
    def update_sql_connection_status(self):
        self.conn = pymysql.connect(
            host="127.0.0.1",  # 主机地址
            user="root",  # 用户名
            passwd="root",  # 密码
            port=3306,  # 端口
            db="user_data"  # 数据库名称
        )
    # 通过产品序列号查找产品信息
    def get_product_infor(self, input_id):
        self.update_sql_connection_status()
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            search = ("select items_input_address,items_output_address,items_result, items_errorcount, items_errorinfor, detect_time from items where"
                      + " query_id = \"" + input_id + "\"")
            cursor.execute(search)
            return cursor.fetchall()

        except Exception as e:
            print("Database exception: ", e)

    # 通过报告序列号查找产品信息
    def get_product_infor_by_report_id(self, input_id):
        self.update_sql_connection_status()
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            search = ("select items_input_address,items_output_address,items_result, items_errorcount, items_errorinfor, detect_time from items where"
                      + " query_id = (select product_number from reports where report_number = \'" + input_id + "\')")
            cursor.execute(search)
            return cursor.fetchall()

        except Exception as e:
            print("Database exception: ", e)

    # 通过报告序列号获取报告信息
    def get_report_time_by_report_id(self, input_id):
        self.update_sql_connection_status()
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            search = "select product_number,download_time from reports where report_number = \'" + input_id + "\';"
            cursor.execute(search)
            return cursor.fetchall()

        except Exception as e:
            print("Database exception: ", e)

    # 通过产品id查询存在的检测报告
    def get_report_id_from_product_id(self, input_id):
        self.update_sql_connection_status()
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            search = "select report_number,download_time from reports where product_number = \'" + input_id + "\';"
            cursor.execute(search)
            return cursor.fetchall()

        except Exception as e:
            print("Database exception: ", e)
    # 修改用户密码
    def update_user_password(self, username, new_password):
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            new_password = self.crypt_password(new_password)
            update = ("update login_infor set pass_word = \'" + new_password + "\' where user_name = \'" + username + "\';")
            cursor.execute(update)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error infor: {e}")

    # 获取指定数据表数据
    def get_table_data(self, table_name):
        self.update_sql_connection_status()
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            if table_name == 'items':
                # 单独查询通道
                search = ("select items_id,query_id,items_name,"
                          "items_input_address,items_output_address,"
                          "items_result,items_errorcount,items_errorinfor,"
                          "items_type,detect_time from " + table_name + ";")
            else:
                search = "select * from " + table_name + ";"
            cursor.execute(search)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error : {e}")

    # 获取数据表字段信息
    def get_tabel_columns(self,tabel_name):
        self.update_sql_connection_status()
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            get = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = \'" + tabel_name + "\' order by ORDINAL_POSITION;"
            cursor.execute(get)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error : {e}")


    # 删除单一数据
    def delete_one_data(self,tabel_name,header,data_name,data_id):
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            update = "update " + tabel_name + " set " + header + " = ''" + " where " + data_name + " = " + data_id + ";"
            cursor.execute(update)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error : {e}")

    # 修改数据
    def modify_one_data(self,tabel_name,header,data_name,data_id,tabel_data):
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            if header == 'pass_word' and tabel_name == 'login_infor':
                tabel_data = self.crypt_password(tabel_data)
                update = "update " + tabel_name + " set " + header + " = \'" + tabel_data + "\' where " + data_name + " = " + data_id + ";"
            else:
                update = "update " + tabel_name + " set " + header + " = " + tabel_data + " where " + data_name + " = " + data_id + ";"
            cursor.execute(update)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error : {e}")

    # 添加数据
    def add_data(self, table_name, data_set):
        # 创建浮标
        cursor = self.conn.cursor()
        keys = list(data_set.keys())
        values = list(data_set.values())
        if table_name == 'login_infor':
            values[1] = self.crypt_password(values[1])
            insert = ("insert into login_infor(" + keys[0] + ","
                      + keys[1] + "," + keys[2] + ","
                      + keys[3] + "," + keys[4] + ","
                      + keys[5] + ") values(\'" + values[0] + "\',\'"
                      + values[1] + "\',\'" + values[2] + "\',\'" + values[3]
                      + "\',\'" + values[4] + "\',\'" + values[5] + "\');")
        elif table_name == 'feedback':
            insert = ("insert into feedback(" + keys[0] + ","
                      + keys[1] + "," + keys[2] + ") values(\'" + values[0] + "\',\'"
                      + values[1] + "\',\'" + values[2] + "\');")
        elif table_name == 'reports':
            insert = ("insert into reports(" + keys[0] + ","
                      + keys[1] + "," + keys[2] + ") values(\'" + values[0] + "\',\'"
                      + values[1] + "\',\'" + values[2] + "\');")
        else:
            insert = ("insert into items(" + keys[0] + ","
                      + keys[1] + "," + keys[2] + ","
                      + keys[3] + "," + keys[4] + ","
                      + keys[5] + ',' + keys[6] + ',' + keys[7] + keys[8] + ") values(\'" + values[0] + "\',\'"
                      + values[1] + "\',\'" + values[2] + "\',\'" + values[3]
                      + "\',\'" + values[4] + "\',\'" + values[5] + "\',\'" + values[6]
                      + "\',\'" + values[7] + "\',\'" + values[8] + "\');")
        try:
            cursor.execute(insert)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error {e}")

    # 用户登录模块
    def user_login(self, input_user_name, input_pass_word):
        # 创建浮标
        cursor = self.conn.cursor()
        try:
            # sql查询语句
            search = ("select user_name,pass_word,position,times,email from " + self.table_name
                      + " where user_name = \""
                      + input_user_name + "\";")
            # 执行sql
            cursor.execute(search)
            # 结果临时存储在tmp
            tmp = cursor.fetchall()
            # 密码验证
            if self.pass_hash.verify(tmp[0][1], input_pass_word):
                # 判断tmp 如果成功后，存储用户信息
                if len(tmp) > 0:
                    self.username = tmp[0][0]
                    self.password = tmp[0][1]
                    self.position = tmp[0][2]
                    self.times = tmp[0][3]
                    self.email = tmp[0][4]

                    # 执行更新
                    self.update_user_login_times()
                    return True
            return False

        except Exception as e:
            print("Database exception: ", e)

# 数据分析功能
class Data_analysis:
    def __init__(self):
        # 数据表
        self.data_source = ""
        # 数据
        self.data_set = tuple()
        # 图片保存路径
        self.save_path = "data_analysis/"
        # 图片对象路径
        self.img1 = ""
        self.img2 = ""
        self.img3 = ""
        self.img4 = ""

    # 用户数据分析
    def user_data_analysis(self):
        # 计算用户和管理员比例
        plt.figure(figsize=(7,5))
        m_data = 0
        u_data = 0
        for users in self.data_set:
            for _ in range(6,len(users)):
                if users[_] == "Manager":
                    m_data += 1
                else:
                    u_data += 1

        x = numpy.array(["Manager","User"])
        y = numpy.array([m_data,u_data])
        plt.title("User ratio")
        plt.bar(x,y,color = ["blue","green"])
        plt.savefig(self.save_path + "user_data_1.png",dpi=300)
        self.img1 = self.save_path + "user_data_1.png"

        # 计算当月活跃的用户以及所在整体用户比例
        plt.figure(figsize=(7, 5))
        current_month = datetime.now().month
        current_year = datetime.now().year
        active_users = 0
        all_data = len(self.data_set)
        for users in self.data_set:
            for _ in range(5,len(users) - 1):
                if eval((users[_].split('-'))[1]) == current_month and eval((users[_].split('-'))[0]) == current_year:
                    active_users += 1

        percentage = (active_users / all_data) * 100
        y = numpy.array([percentage,all_data])
        plt.pie(y,labels=["Active users","Opposite"],colors=['#d5695d','#5d8ca8'],explode=(0.1, 0),autopct='%.2f%%')
        plt.title('The proportion of current month active users')
        plt.savefig(self.save_path + "user_data_2.png",dpi=300)
        self.img2 = self.save_path + "user_data_2.png"

        # 计算最近5年中活跃用户数量以及比例
        plt.figure(figsize=(7, 5))
        active_years_num = [0,0,0,0,0]
        last_five_year = []
        percentage_year = [0,0,0,0,0]

        current_year = datetime.now().year
        for _ in range(5):
            last_five_year.append(str(current_year - _))

        for users in self.data_set:
            for _ in range(5,len(users) - 1):
                for i in range(len(last_five_year)):
                    if (users[_].split('-'))[0] == last_five_year[i]:
                        active_years_num[i] += 1

        for _ in range(len(active_years_num)):
            percentage_year[_] = (active_years_num[_] / all_data) * 100

        df = pandas.DataFrame({
            "Quantity":active_years_num,
            "Year":last_five_year
        })

        ns.set_theme(style="whitegrid")
        ns.barplot(x='Year',y='Quantity',hue='Year',data=df)
        plt.xlabel('Year')
        plt.ylabel('Quantity')
        plt.title('The number of active users in the last five years')
        plt.savefig(self.save_path + "user_data_3.png", dpi=300)
        self.img3 = self.save_path + "user_data_3.png"

        # 计算当年所有月份活跃的用户
        plt.figure(figsize=(7, 5))
        year_data = []
        for _ in range(12):
            year_data.append(0)

        year_labels = list(calendar.month_name)[1:]
        for users in self.data_set:
            for _ in range(5,len(users) - 1):
                if eval((users[_].split('-'))[0]) == current_year:
                    for i in range(12):
                        if eval((users[_].split('-'))[1]) == i + 1:
                            year_data[i] += 1


        y_array = range(1,13)
        df = pandas.DataFrame({
            "data": year_data,
            "labels": y_array,
            "Years":year_labels
        })
        print(year_data)
        print(y_array)
        ns.lineplot(data=df,y='data',x='labels',linewidth=2)
        plt.title(f'Active user trend in {current_year}')
        plt.xlabel('Months (Jan to Dec)')
        plt.savefig(self.save_path + "user_data_4.png", dpi=300)
        self.img4 = self.save_path + "user_data_4.png"

    # 产品数据分析
    def product_data_analysis(self):
        # 计算当月产品合格比例和不合格比例
        plt.figure(figsize=(7, 5))
        current_month_pd = []
        current_month = datetime.now().month
        current_year = datetime.now().year
        for pd in self.data_set:
            for _ in range(9, len(pd)):
                if eval((pd[_].split('-'))[1]) == current_month or eval((pd[_].split('-'))[0]) == current_year:
                    current_month_pd.append(pd)

        pd_failed = 0
        pd_passed = 0
        all_num = len(current_month_pd)

        for index in current_month_pd:
            if index[5] == 'Fail':
                pd_failed += 1
            else:
                pd_passed += 1

        percentage_pd1 = (pd_failed / all_num) * 100
        percentage_pd2 = (pd_passed / all_num) * 100
        y = numpy.array([percentage_pd1,percentage_pd2])
        current_month_text = calendar.month_name[current_month]
        plt.pie(y, labels=[f"Defect rate in {current_month_text}", f"Pass rate in {current_month_text}"], colors=['#d5695d', '#5d8ca8'], explode=(0.1, 0),
                autopct='%.2f%%')
        plt.title('The proportion of PCB quality for the current month')
        plt.savefig(self.save_path + "product_data_1.png", dpi=300)
        self.img1 = self.save_path + "product_data_1.png"
        print(self.data_set[0])

        # 计算五年内pcb检测入库数量
        plt.figure(figsize=(7, 5))
        last_years_labels = []
        last_years_values = [0,0,0,0,0]

        for _ in range(5):
            last_years_labels.append(int(current_year))
            current_year -= 1
        for pd in self.data_set:
            for _ in range(9, len(pd)):
                for i in range(len(last_years_labels)):
                    if eval((pd[_].split('-'))[0]) == last_years_labels[i]:
                        last_years_values[i] += 1
                        break

        df = pandas.DataFrame({
            "num": last_years_values,
            "Year": last_years_labels,
            "years":last_years_labels
        })
        ns.set_theme(style="whitegrid")
        ns.barplot(x='Year', y='num', hue='years', data=df)
        plt.xlabel('The past five years')
        plt.ylabel('Quantity in stock')
        plt.title('The number of PCBs stored in the databases over the past five years')
        plt.savefig(self.save_path + "product_data_2.png", dpi=300)
        self.img2 = self.save_path + "product_data_2.png"


        # 计算五年内缺陷的pcb数量和通过数量
        plt.figure(figsize=(7, 5))
        current_year = datetime.now().year
        last_five_years_labels = []
        last_five_years_values = []
        for _ in range(5):
            tmp = [str(current_year - _),'Passed']
            last_five_years_labels.append(tmp)

        for _ in range(5):
            k = [0,0]
            last_five_years_values.append(k)
        for pd in self.data_set:
            for _ in range(9, len(pd)):
                for i in range(len(last_five_years_labels)):
                    if eval((pd[_].split('-'))[0]) == eval(last_five_years_labels[i][0]) and (pd[5]) == 'Fail':
                        last_five_years_values[i][0] += 1
                    elif eval((pd[_].split('-'))[0]) == eval(last_five_years_labels[i][0]) and (pd[5]) == 'Pass':
                        last_five_years_values[i][1] += 1

        df_records = []
        for i in range(len(last_five_years_values)):
            for j in range(len(last_five_years_labels[i])):
                df_records.append({
                    "values": last_five_years_values[i][j],
                    "labels": last_five_years_labels[i][j],
                    "simple": f"{last_five_years_labels[i][0]}",
                    'index':i
                })

        df = pandas.DataFrame(df_records)

        ns.set_theme(style="whitegrid")
        ns.barplot(x='simple', y='values',hue='labels',data=df)

        for labels in df['labels']:
            sub_df1 = df[df['labels'] == 'Passed'].sort_values('index')
            plt.plot(sub_df1['index'], sub_df1['values'], marker='o',label=labels)
            sub_df2 = df[df['labels'] != 'Passed'].sort_values('index')
            plt.plot(sub_df2['index'], sub_df2['values'], marker='o', label=labels)

        plt.xlabel('Years')
        plt.ylabel('Quantity')
        plt.title('Defective samples and pass samples in 5 years')
        plt.tight_layout()
        plt.savefig(self.save_path + "product_data_3.png", dpi=300)
        self.img3 = self.save_path + "product_data_3.png"

        # 统计今年的pcb缺陷类别的数量以及通过数量
        plt.figure(figsize=(8, 6))
        current_passed = 0
        defect_labels = ['Missing\nhole','Mouse\nbite','Open\ncircuit','Short','Spur','Spurious\ncopper','Pass\nnumber']
        defect_values = list(range(6))

        for pd in self.data_set:
            for _ in range(5, len(pd) - 4):
                if pd[_] != 'Fail':
                    current_passed += 1
            for _ in range(6, len(pd) - 3):
                tmp = ast.literal_eval(pd[_])
                for i in range(len(tmp)):
                    if tmp[i] != ' ':
                        defect_values[i] += 1
        defect_values.append(current_passed)

        df = pandas.DataFrame({
            "values": defect_values,
            "labels": defect_labels,
        })
        current_year = datetime.now().year

        ns.set_theme(style="whitegrid")
        ns.barplot(x='values', y='labels', data=df)
        plt.ylabel('Defects')
        plt.xlabel('Quantity')
        plt.title(f'The number of PCB defects and the number of passed ones in {current_year}')
        plt.savefig(self.save_path + "product_data_4.png", dpi=300)
        self.img4 = self.save_path + "product_data_4.png"

    # 数据分析和生成
    def generate_analysis(self):
        if self.data_source == 'login_infor':
            self.user_data_analysis()
        else:
            self.product_data_analysis()









