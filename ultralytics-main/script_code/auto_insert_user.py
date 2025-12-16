import random
import string
from datetime import datetime
import pymysql

# 自动生成用户数据导入本地数据库脚本
# 本地数据库配置
# 主机名
host="127.0.0.1"
# 用户名
user="root"
# 密码
passwd="ai5201314"
# 端口号
port=3306
# 数据库名称
db="user_data"
# 数据表名称
table_name = "login_infor"
# 生成批次数量
num = 50
# 生成比例
m_user = 2
n_user = 8
# 实际生成参数
batch_m_user = 0
batch_n_user = 0
# 范围和时间参数
d_max_times = 500
d_min_times = 1
d_date_year = []
d_date_month = ['12','11','10','9','8','7','6','5','4','3','2','1']
d_date_max_day = 29
d_date_max_hours = 24
d_date_max_mins = 59
d_date_max_seconds = 50
d_position = ['User','Manager']
d_email_name = ['@gmail.com','@qq.com','@outlook.com']

# 计算生成比例大小
def calculate_proportion():
    global batch_m_user, batch_n_user
    if m_user + n_user != 10:
        print('The proportion parameter is incorrect')
        return False

    batch_m_user = round(num * (m_user / 10))
    batch_n_user = round(num * (n_user / 10))
    print(batch_m_user, batch_n_user)
    print('The proportion parameter is correct')
    return True

# 初始化时间参数范围
def auto_generate_year(k = 5):
    current_year = datetime.now().year
    for _ in range(k):
        d_date_year.append(str(current_year - _))

# 测试连接
def test_connection():
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            passwd=passwd,
            port=port,
            db=db
        )
        print(conn)
    except Exception as error_infor:
        print("Database connection error")
        print(error_infor)

# 随机生成用户名
def generate_username():
    letters = string.ascii_letters
    digits = string.digits
    char = letters + digits
    username = ''.join(random.choices(char, k = 5))
    return username

# 随机生成密码
def generate_password():
    passwd =  ''.join(random.choices(string.octdigits, k = 4))
    return passwd

# 随机生成邮箱号
def generate_email():
    email =  ''.join(random.choices(string.ascii_uppercase, k = 6))
    return email + random.choice(d_email_name)

# 随机生成次数
def generate_times():
    return random.randint(d_min_times,d_max_times)

# 随机生成时间
def generate_date():
    g_year = random.choice(d_date_year)
    g_month = random.choice(d_date_month)
    g_day = random.randint(10,d_date_max_day)
    date = (str(g_year) + "-" + str(g_month) + "-" + str(g_day) + " "
            + str(random.randint(10,d_date_max_hours)) + ":" + str(random.randint(10,d_date_max_mins))) + ":" + str(random.randint(10,d_date_max_seconds))
    return date

# 用户名验证
def if_username_valid(username):
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            passwd=passwd,
            port=port,
            db=db
        )

        cursor = conn.cursor()
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
def if_email_address_valid(address):
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            passwd=passwd,
            port=port,
            db=db
        )

        cursor = conn.cursor()
        check = "select * from login_infor where email = \'" + address + "\';"
        cursor.execute(check)
        result = cursor.fetchall()
        if len(result) == 0:
            return True
        else:
            return False

    except Exception as e:
        print("Database exception: ", e)

# 自动导入
def auto_import():
    conn = pymysql.connect(
        host=host,
        user=user,
        passwd=passwd,
        port=port,
        db=db
    )
    cursor = conn.cursor()
    for _ in range(batch_n_user):
        while True:
            username = generate_username()
            address = generate_email()
            if if_username_valid(username) and if_email_address_valid(address):
                break
        insert = ("insert into " + table_name
                  + "(user_name, pass_word, email, times, last_login, position)"
                  + "values(\"" + username + "\",\"" + generate_password() + "\",\""
                  + address + "\"," + str(generate_times()) + ",\"" + generate_date() + "\",\"" + d_position[0] + "\")")
        cursor.execute(insert)
        conn.commit()
        print(f"execute {_ + 1} ")

    for _ in range(batch_m_user):
        while True:
            username = generate_username()
            address = generate_email()
            if if_username_valid(username) and if_email_address_valid(address):
                break
        insert = ("insert into " + table_name
                  + "(user_name, pass_word, email, times, last_login, position)"
                  + "values(\"" + username + "\",\"" + generate_password() + "\",\""
                  + address + "\"," + str(generate_times()) + ",\"" + generate_date() + "\",\"" + d_position[1] + "\")")
        cursor.execute(insert)
        conn.commit()
        print(f"execute {_ + 1} ")


if __name__ == '__main__':
    if calculate_proportion():
        auto_generate_year()
        auto_import()



