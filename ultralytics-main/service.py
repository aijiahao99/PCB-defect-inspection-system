import ast
import os.path
import uuid
from threading import Thread
from flask import Flask, request, jsonify
import sql,detect,infer
# 创建 flask 服务器
FLASK_APP = Flask(__name__)
# 实体化数据库对象
CONNECT_MYSQL = sql.Sql_connect()
# 初始化模型
run_predict = detect.model_predict()
# 初始化数据分析对象
data_object = sql.Data_analysis()
# 当前加载的数据库表名
data_table_name = ""
# 当前批次数据
batch_data_set = None
# 调用api服务
@FLASK_APP.route('/call_api_model',methods=['POST'])
def call_api():
    data = request.json
    user_text = data.get('text_line')
    model_name = data.get('model_name')
    answer_text = infer.call_aliyun_model(user_text,model_name)
    return jsonify({'status':"pass",'answer_text':answer_text})

# 调用api服务
@FLASK_APP.route('/call_api_model_assessment',methods=['POST'])
def call_api_assessment():
    data = request.json
    result_text = data.get('result_line')
    model_name = data.get('model_name')
    answer_text = infer.call_aliyun_api_assessment(model_name,result_text)
    return jsonify({'status':"pass",'answer_text':answer_text})

# 删除整行数据服务
@FLASK_APP.route('/delete_row',methods=['POST'])
def delete_row():
    data = request.json
    name = data.get('row_name')
    id = data.get('row_id')
    if CONNECT_MYSQL.delete_row_table_data(data_table_name,name,id):
        return jsonify({"status": "Pass"})
    return jsonify({'status':"100"})
# 删除整行数据服务
@FLASK_APP.route('/delete_all',methods=['POST'])
def delete_all():
    if CONNECT_MYSQL.delete_all_data(data_table_name):
        return jsonify({"status": "Pass",'infor':"Operation successful"})
    return jsonify({'status':"100"})

# 获取默认路径服务
@FLASK_APP.route('/get_default_path',methods=['POST'])
def get_default_path():
    return jsonify({"status": "Pass","path":run_predict.result_save_address})

# 获取登录路径服务
@FLASK_APP.route('/login',methods=['POST'])
def get_user_account():
    user_data = request.json
    # 获取用户账号
    get_username = user_data.get('username')
    get_password = user_data.get('password')
    # 管理员后门(开发和测试使用)
    if get_username == 'admin' and get_password == 'admin':
        CONNECT_MYSQL.position = "Manager"
        return jsonify({"status": "Pass", "address":"-", "times": "-",
                        "level": CONNECT_MYSQL.position})
    # 判断是否为空
    if len(get_username) == 0 or len(get_password) == 0:
        return jsonify({"status": "100","error":"Account information is empty"})
    # 判断是否用户账号存在
    if CONNECT_MYSQL.user_login(get_username,get_password):
        return jsonify({"status": "Pass","address":CONNECT_MYSQL.email,"times":CONNECT_MYSQL.times,"level":CONNECT_MYSQL.position})
    else:
        # 用户账号不存在
        return jsonify({"status": "100","error":"Account does not exist"})

# 注册服务
@FLASK_APP.route('/register',methods=['POST'])
def get_user_register():
    user_data = request.json
    # 获取注册账号
    get_register_username = user_data.get('username')
    get_register_password = user_data.get('password')
    get_register_address = user_data.get('address')
    get_register_type = user_data.get('type')
    # 用户名验证
    if not CONNECT_MYSQL.if_username_valid(get_register_username):
        return jsonify({"status": "100", "error": "The username is duplicated"})
    # 邮箱地址验证
    if not CONNECT_MYSQL.if_email_address_valid(get_register_address):
        return jsonify({"status": "100", "error": "The email address has already been registered"})
    # sql规范验证
    status_infor = CONNECT_MYSQL.user_register(get_register_username,get_register_password,get_register_address,get_register_type)
    if status_infor == 'pass':
        return jsonify({"status": "Pass", "error": "None"})
    else:
        return jsonify({"status": "100", "error": status_infor})

# 反馈信息提交服务
@FLASK_APP.route('/feedback',methods=['POST'])
def submit_user_feedback():
    feedback_data = request.json
    # 获取反馈信息
    get_feedback_infor = feedback_data.get('content')
    get_feedback_name = feedback_data.get('name')

    if len(get_feedback_name) == 0 or len(get_feedback_infor) == 0:
        return jsonify({"status": "100", "error": "No feedback information is available"})
    else:
        CONNECT_MYSQL.user_feedback(get_feedback_name,get_feedback_infor)
        return jsonify({"status": "Pass", "error": "None"})

# 主界面更新服务
@FLASK_APP.route('/main_window',methods=['POST'])
def check_user_type():
    if CONNECT_MYSQL.position == "User":
        return jsonify({"status": "100", "error": "User"})
    return jsonify({"status": "Pass", "error": "Manager"})

# 模型运行服务
@FLASK_APP.route('/model',methods=['POST'])
# 调用模型并且获取结果
def calling_model():
    input_img_address = request.json
    get_img_address = input_img_address.get('address')
    get_img_output_address = input_img_address.get('output_address').replace('\\','/')
    # 设置模型参数
    run_predict.imgs_address = get_img_address
    run_predict.result_save_address = get_img_output_address
    run_predict.save_filename = f"{uuid.uuid4()}"
    # 获取到相关结果
    get_output_address = run_predict.run_model()
    get_data = str(run_predict.data[5:11])
    get_result = run_predict.qualified
    get_img_name = run_predict.imgs_name
    get_img_type = run_predict.imgs_type
    get_report_path = run_predict.report_path
    get_id = run_predict.init.product_code

    if get_output_address == 'None':
        return jsonify({"status": "100", "error": "..."})
    return jsonify({"status": "Pass",
                    "address": get_output_address,
                   "data_set":get_data,"result":get_result,"imgn":get_img_name,"imgt":get_img_type,
                    "report_path":get_report_path,"id":get_id})


# 实时检测服务
@FLASK_APP.route('/camera',methods=['POST'])
def open_cam_model():
    run_predict.real_time_detect()
    return jsonify({"status":"Pass"})

# 下载报告服务
@FLASK_APP.route('/download',methods=['POST'])
def download():
    save_path = request.json
    # 判断路径有效
    if os.path.isdir(save_path.get('path')):
        run_predict.report_path = save_path.get('path').replace('\\','/')
        run_predict.download_report(save_path.get('id'))
        return jsonify({"status":"Pass"})
    else:
        return jsonify({"status":"100"})

# 搜索产品信息服务
@FLASK_APP.route('/search',methods=['POST'])
def search():
    search_id = request.json
    get_mode = search_id.get('mode')
    if get_mode == 'product':
        get_result = CONNECT_MYSQL.get_product_infor(search_id.get('id'))
        get_report = CONNECT_MYSQL.get_report_id_from_product_id(search_id.get('id'))
        if len(get_result) != 0:
            result = list(get_result[0])
            report_id = ""
            download_date = ""
            if len(get_report) != 0:
                report_id = get_report[0][0]
                download_date = get_report[0][1]

            return jsonify({"status": "ok", "detect_img": result[0], "result_img": result[1], "result": result[2],
                            "defect_num": result[3], "defect_infor": result[4], "detect_time": result[5],
                            "report_id": report_id, "download": download_date})

    else:
        get_result = CONNECT_MYSQL.get_product_infor_by_report_id(search_id.get('id'))
        get_report = CONNECT_MYSQL.get_report_time_by_report_id(search_id.get('id'))
        if len(get_result) != 0:
            result = list(get_result[0])
            product_id = ""
            download_date = ""
            if len(get_report) != 0:
                product_id = get_report[0][0]
                download_date = get_report[0][1]

            return jsonify({"status": "ok", "detect_img": result[0], "result_img": result[1], "result": result[2],
                            "defect_num": result[3], "defect_infor": result[4], "detect_time": result[5],
                            "report_id": search_id.get('id'),"product_id":product_id
                               ,"download": download_date})


    return jsonify({'status': '100',"mode":get_mode})

# 初始化报告数据结构
def reset_data():
    for i in range(5,12):
        run_predict.data[i][1] = '0'
        run_predict.data[i][2] = 'Pass'

# 重新下载报告服务
@FLASK_APP.route('/re_download',methods=['POST'])
def re_download():
    data = request.json
    run_predict.data_set = ast.literal_eval(data.get("dataset"))
    run_predict.qualified = data.get('output')
    CONNECT_MYSQL.product_code = data.get('product_id')
    img1 = data.get('img1')
    img2 = data.get('img2')
    try:
        infor =  run_predict.re_download_report(CONNECT_MYSQL.product_code,img1,img2)
        print(infor)
        return jsonify({'status':'Pass',"id":infor[0],"time":infor[1]})
    except Exception as e:
        print(e)
        return jsonify({'status':'100'})

# 修改密码服务
@FLASK_APP.route('/change_password',methods=['POST'])
def change():
    data = request.json
    username = data.get('username')
    password = data.get('new_password')
    password_n = data.get('confirm_password')
    if len(password) == 0 or len(password_n) == 0:
        return jsonify({'status': '100', "error": "Information gap !"})
    elif password_n != password:
        return jsonify({'status': '100',"error":"Password mismatch !"})
    elif CONNECT_MYSQL.update_user_password(username,password):
        return jsonify({'status': 'Pass',"infor":"Password modification is successful. Please log in again"})
    return jsonify({'status': '100'})

@FLASK_APP.route('/delete_user',methods=['POST'])
def delete():
    if CONNECT_MYSQL.user_delete():
        return jsonify({'status': 'Pass','infor':"Account cancellation successful. Please Log in again"})
    return jsonify({'status': '100'})

# 获取数据库数据服务
@FLASK_APP.route('/get_database_data',methods=['POST'])
def get():
    data = request.json
    types = data.get('type')
    global data_table_name
    if types == 'User data':
        raw_dataset = CONNECT_MYSQL.get_table_data('login_infor')
        raw_labels = CONNECT_MYSQL.get_tabel_columns('login_infor')
        chinese_labels = ['User ID','Username','Password','Email address','Number of visits','Login time','Type']
        data_table_name = "login_infor"
    elif types == 'Product data':
        raw_dataset = CONNECT_MYSQL.get_table_data('items')
        raw_labels = CONNECT_MYSQL.get_tabel_columns('items')
        chinese_labels = ['Product ID', 'Product serial number', 'Image name', 'Sample Address', 'Result address', 'Final result', 'Number of defects','Defect information','Image type','Detect time']
        data_table_name = "items"
    elif types == 'Report data':
        raw_dataset = CONNECT_MYSQL.get_table_data('reports')
        raw_labels = CONNECT_MYSQL.get_tabel_columns('reports')
        chinese_labels = ['Report ID', 'Report serial number', 'Product serial number','Download time']
        data_table_name = "reports"
    else:
        raw_dataset = CONNECT_MYSQL.get_table_data('feedback')
        raw_labels = CONNECT_MYSQL.get_tabel_columns('feedback')
        chinese_labels = ['Feedback ID', 'Username', 'Feedback information', 'Feedback time']
        data_table_name = "feedback"

    if len(raw_dataset) != 0:
        return jsonify({'status': 'Pass','zn_labels':str(chinese_labels),'row':len(raw_dataset),'col':len(raw_dataset[0]),'set':str(raw_dataset),'labels':str(raw_labels)})
    return jsonify({'status':'100'})

# 删除数据服务
@FLASK_APP.route('/delete_database_data',methods=['POST'])
def delete_data():
    input_data = request.json
    header = input_data.get('header')
    item_id = input_data.get('row_id')
    item_name = input_data.get('row_name')
    global data_table_name
    if CONNECT_MYSQL.delete_one_data(data_table_name,header,item_name,item_id):
        return jsonify({'status': 'Pass','infor':"Operation successful"})
    return jsonify({'status': '100'})

# 修改数据服务
@FLASK_APP.route('/modify_database_data',methods=['POST'])
def modify_data():
    input_data = request.json
    header = input_data.get('header')
    item_id = input_data.get('row_id')
    item_name = input_data.get('row_name')
    item_data = input_data.get('row_data')
    global data_table_name
    if type(item_data) is str:
        item_data = "'" + item_data + "'"
    if CONNECT_MYSQL.modify_one_data(data_table_name, header, item_name, item_id, item_data):
        return jsonify({'status': 'Pass', 'infor': "Operation successful"})
    return jsonify({'status': '100'})

# 添加数据服务
@FLASK_APP.route('/add_database_data',methods=['POST'])
def add():
    new_data = request.json
    global data_table_name
    if CONNECT_MYSQL.add_data(data_table_name, new_data):
        return jsonify({'status': 'Pass', 'infor': "Operation successful"})
    return jsonify({'status': '100','infor':"Data addition failed"})

# 批量检测下路径验证服务
@FLASK_APP.route('/batch_detect_path',methods=['POST'])
def batch_path():
    path = request.json
    path1 = path.get('target')
    path2 = path.get('result')
    if not os.path.isdir(path1):
        return jsonify({'status': '100','infor':"The target path is incorrect"})
    if not os.path.isdir(path2):
        return jsonify({'status': '100', 'infor': "The result path is incorrect"})
    return jsonify({'status': 'pass'})

# 批量检测服务
@FLASK_APP.route('/batch_detect',methods=['POST'])
def batch_detection():
    global batch_data_set
    path = request.json
    file = path.get('file_path').replace('\\', '/')
    output_path = path.get('output_path').replace('\\', '/')
    if output_path.split('/')[-1] != ' ':
        output_path += '/'
    # 设置模型参数
    run_predict.imgs_address = file
    run_predict.result_save_address = output_path
    run_predict.save_filename = f"{uuid.uuid4()}"
    run_predict.batch_run_model()
    batch_data_set = run_predict.last_batch_data
    return jsonify({'status': 'pass'})

# 下载报告请求
@FLASK_APP.route('/batch_download_report',methods=['POST'])
def report_get():
    index = request.json
    if run_predict.batch_download_report(index_id=index):
        return jsonify({'status': 'pass'})
    return jsonify({'status': '100'})

# 下载所有报告请求
@FLASK_APP.route('/batch_download_all_report',methods=['POST'])
def report_get_all():
    if run_predict.batch_download_report(mode='mult'):
        return jsonify({'status': 'pass'})
    return jsonify({'status': '100'})

# 结果数据请求
@FLASK_APP.route('/batch_result',methods=['POST','GET'])
def result_get():
    return jsonify({'set': str(batch_data_set)})

# 结果数据清除
@FLASK_APP.route('/batch_result_clear',methods=['POST','GET'])
def result_clear():
    global batch_data_set
    if len(run_predict.last_batch_data) > 0:
        run_predict.last_batch_data.clear()
        batch_data_set = None
    return jsonify({'status': 'pass'})


# 数据分析服务
@FLASK_APP.route('/data_review',methods=['POST'])
def data_any():
    data_object.data_source = data_table_name
    data_result =  CONNECT_MYSQL.get_table_data(data_table_name)
    if data_result:
        data_object.data_set = data_result
        data_object.generate_analysis()
    else:
        return jsonify({'status': '100',"infor":"The data is empty !"})

    return jsonify({'status': 'pass','imgs1':data_object.img1,'imgs2':data_object.img2,'imgs3':data_object.img3,'imgs4':data_object.img4})

# 运行flask服务
def run_service():
    FLASK_APP.run(host="127.0.0.1", port=5050, debug=False, use_reloader=False)

# 服务线程开启
flask_thread = Thread(target=run_service, daemon=True)
flask_thread.start()
