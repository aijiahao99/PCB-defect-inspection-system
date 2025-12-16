# 执行初始化和运行login界面文件
import sys
import object,sys_function

class Run_system:
    def __init__(self):
        # 创建窗口
        object.MAIN_WIN.show()
        # 安全退出以及释放资源
        sys.exit(object.APP.exec_())

# 导入库
if __name__ == "__main__":
    # 初始化对象功能类 （登录，注册，反馈界面）
    # 静态界面
    sys_login = sys_function.Login_fun()
    sys_sys_infor = sys_function.Sys_infor()
    sys_register = sys_function.Register_fun()
    sys_feedback = sys_function.Feedback_fun()
    sys_detection = sys_function.Detect_mainwindow()
    sys_modification = sys_function.Password_modification()
    sys_add = sys_function.Add_data()
    sys_auto = sys_function.Auto_detection()
    window = Run_system()
