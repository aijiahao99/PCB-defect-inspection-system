# 自动生成和导入产品缺陷信息 (生成的数据不实，仅供测试和开发使用)
import random
import string
from datetime import datetime
import pymysql
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
table_name = "items"
# 结果文件名称
save_filename = 'output'
# 检测结果
result = ['Pass','Fail']
# 有效图片类型
regular = ['jpg', 'png', 'jpeg']
# 缺陷类别
defects = ['Missing hole','Mouse bite','Open circuit','Short','Spur','Spurious copper']
# 生成批次数量
num = 100
# 生成比例
passed = 1
failed = 9
# 实际生成参数
batch_pass = 0
batch_fail = 0
# 时间参数
d_date_year = []
d_date_month = ['12','11','10','9','8','7','6','5','4','3','2','1']
d_date_max_day = 29
d_date_max_hours = 24
d_date_max_mins = 59
d_date_max_seconds = 50

# 初始化时间参数范围
def auto_generate_year(k = 5):
    current_year = datetime.now().year
    for _ in range(k):
        d_date_year.append(str(current_year - _))

# 随机生成序列号模块
def auto_generate_code(groups = 4, chars_per = 5):
    serial = []
    for _ in range(groups):
        group = ''.join(random.choices(string.ascii_uppercase + string.digits, k=chars_per))
        serial.append(group)
    g_id = '-'.join(serial)
    # 返回序列号
    return 'test-'+g_id

# 随机生成时间
def generate_date():
    g_year = random.choice(d_date_year)
    g_month = random.choice(d_date_month)
    g_day = random.randint(10,d_date_max_day)
    date = (str(g_year) + "-" + str(g_month) + "-" + str(g_day) + " "
            + str(random.randint(10,d_date_max_hours)) + ":" + str(random.randint(10,d_date_max_mins))) + ":" + str(random.randint(10,d_date_max_seconds))
    return date

# 随机生成缺陷数量和类别
def generate_defects(k = random.randint(1,4)):
    g_defects = [' ',' ',' ',' ',' ',' ']
    g_types = [' ', ' ', ' ', ' ', ' ', ' ']
    for _ in range(k):
        g_defects[random.randint(0,5)] = str(random.randint(1,5))
    for _ in range(len(g_types)):
        if g_defects[_] != ' ':
            g_types[_] = defects[_]
    return [str(g_defects),str(g_types)]

# 随机生成图片名称
def generate_name(k = 5):
    text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=k))
    return text

# 计算生成比例大小
def calculate_proportion():
    global batch_pass, batch_fail
    if passed + failed != 10:
        print('The proportion parameter is incorrect')

    batch_fail = round(num * (failed / 10))
    batch_pass = round(num * (passed / 10))
    print(batch_fail, batch_pass)
    print('The proportion parameter is correct')

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

# 检测并导入数据库
def main():
    conn = pymysql.connect(
        host=host,
        user=user,
        passwd=passwd,
        port=port,
        db=db
    )
    cursor = conn.cursor()
    for _ in range(batch_fail):
        g_products = generate_defects()
        insert = (("insert into " + table_name
                   + "(query_id, items_name, items_input_address,items_output_address, items_result, items_errorcount, items_errorinfor, items_type, detect_time, img_data, img_hash)")
                  + "values(\"" + auto_generate_code() + "\",\"" + generate_name() + "\",\"" + generate_name(15)
                  + "\",\"" + generate_name(15) + "\",\"" + result[1] + "\",\"" + g_products[0] + "\",\"" + g_products[1]
                  + "\",\"" + random.choice(regular) + "\",\"" + generate_date() + "\",\"" + generate_name(20) + "\",\"" + generate_name(9) + "\")")
        #print(insert)

        # 执行并提交
        cursor.execute(insert)
        conn.commit()
        print(f"insert success {_}")

    g_pass_x = [' ',' ',' ',' ',' ',' ']
    g_pass_y = [' ',' ',' ',' ',' ',' ']
    for _ in range(batch_pass):
        insert = (("insert into " + table_name
                   + "(query_id, items_name, items_input_address,items_output_address, items_result, items_errorcount, items_errorinfor, items_type, detect_time, img_data, img_hash)")
                  + "values(\"" + auto_generate_code() + "\",\"" + generate_name() + "\",\"" + generate_name(15)
                  + "\",\"" + generate_name(15) + "\",\"" + result[0] + "\",\"" + str(g_pass_x) + "\",\"" + str(g_pass_y)
                  + "\",\"" + random.choice(regular) + "\",\"" + generate_date() + "\",\"" + generate_name(20) + "\",\"" + generate_name(9) + "\")")

        # 执行并提交
        cursor.execute(insert)
        conn.commit()
        print(f"insert success {_}")


if __name__ == '__main__':
    auto_generate_year()
    calculate_proportion()
    main()