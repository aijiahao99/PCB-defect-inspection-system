import torch
import ast
import os.path
import shutil

import imagehash
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as Img
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from PIL import Image

import sql
import cv2
from ultralytics import YOLO
# 模型预测调用文件
# 包含结果数据处理
class model_predict:
    def __init__(self):
        # 初始化数据库 (测试使用)
        self.init = sql.Sql_connect()
        # 训练好的模型文件 （最佳权重）
        self.best_weights = "runs/train/exp7/weights/best.pt"
        # 被检测的图片地址
        self.imgs_address = "detect_imgs/test2.jpg"
        # 被识别图片名称
        self.imgs_name = None
        # 被识别图片类型
        self.imgs_type = None
        # 被识别图片所在文件
        self.imgs_fold_address = "detect_imgs/"
        # 加载
        self.model = YOLO(self.best_weights)
        # 边框位置
        self.location = []
        # 缺陷数量
        self.result_count = 0
        # 置信度
        self.confidence = []
        # 识别结果的保存路径
        self.result_save_address = "detect_results/"
        # 保存文件名称
        self.save_filename = 'output'
        # 识别结果
        self.result = []
        # 是否合格
        self.qualified = "Pass"
        # 报告存放路径
        self.report_path = "reports/"
        # 结果数据集
        self.data_set = []
        # 创建报告样式对象
        self.style = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkgray),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ('SPAN', (1, 0), (2, 0)),
            ('SPAN', (1, 1), (2, 1)),
            ('SPAN', (1, 2), (2, 2)),
            ('SPAN', (0, 3), (2, 3)),
            ('SPAN', (0, 11), (2, 11)),
            ('SPAN', (1, 12), (2, 12)),
            ('SPAN', (1, 13), (2, 13)),
            ('SPAN', (1, 14), (2, 14)),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ])
        # 初始化图片
        self.img1 = None
        self.img2 = None

        # 初始化数据表格
        self.data = [
            ["Report ID", self.init.auto_generate_report_id()],
            ["Sample image", self.img1],
            ["Result image", self.img2],
            [""],
            ["Detect item", "Quantities", "Result"],
            ["Missing hole", "0", "Pass"],
            ["Mouse bite", "0", "Pass"],
            ["Open circuit", "0", "Pass"],
            ["Short", "0", "Pass"],
            ["Spur", "0", "Pass"],
            ["Spurious copper", "0", "Pass"],
            [" ", " ", " "],
            ["Product serial number", self.init.auto_generate_code()],
            ["Final detect result", self.qualified],
            ["Download report time", str(self.init.auto_generate_time())]
        ]
        # 批量检测数据
        self.last_batch_data = []

    # 验证图片是否存在
    def if_imgs_address_valid(self):
        # 判断是否在该路径中
        if os.path.exists(self.imgs_address):
            return True
        return False

    # 判断有没有生成txt文件，如果没有则没有结果生成
    def if_txt_file_exists(self):
        if os.path.exists(self.result_save_address + self.save_filename + "/labels/" + self.imgs_name + ".txt"):
            return True
        return False

    # 分割和获取图片名称和类型
    def spilt_imgs_infor(self):
        self.imgs_type = self.imgs_address.split(".")[len(self.imgs_address.split(".")) - 1]
        self.imgs_name = (self.imgs_address.split('/')[len(self.imgs_address.split('/')) - 1]).split('.')[0]

    # 读取识别结果在txt文件中
    def read_result(self):
        if self.if_txt_file_exists():
            with open(self.result_save_address + self.save_filename + "/labels/" + self.imgs_name + ".txt") as file:
                for i in file.readlines():
                    # 读取后传值
                    self.result_count += len(list(i.split(' '))[0])
                    self.confidence.append(list(i.split(' '))[len(list(i.split(' '))[0]) - 1])
                    self.location.append(list(i.split(' '))[1:5])
            self.qualified = "Fail"
        else:
            self.qualified = "Pass"


    # 删除指定文件夹
    def remove_dir(self):
        if os.path.exists(self.result_save_address + self.save_filename):
            shutil.rmtree(self.result_save_address + self.save_filename)

    # 重新下载报告
    def re_download_report(self,id,img1_org = None,img2_output = None):
        # 更新报告序列号
        self.data[0][1] = self.init.auto_generate_report_id()
        # 更新下载时间
        self.data[14][1] = str(self.init.auto_generate_time())

        for i in range(5,11):
            self.data[i][2] = 'Pass'

        self.data[12][1] = id

        # 颜色调整
        self.style.add("TEXTCOLOR", (2, 5), (2, 5), colors.green)
        self.style.add("TEXTCOLOR", (2, 6), (2, 6), colors.green)
        self.style.add("TEXTCOLOR", (2, 7), (2, 7), colors.green)
        self.style.add("TEXTCOLOR", (2, 8), (2, 8), colors.green)
        self.style.add("TEXTCOLOR", (2, 9), (2, 9), colors.green)
        self.style.add("TEXTCOLOR", (2, 10), (2, 10), colors.green)
        self.style.add("TEXTCOLOR", (1, 13), (1, 13), colors.green)
        self.data[13][1] = 'Pass'

        # 修改数据
        row = 5
        for i in range(len(self.data_set)):
            if self.data_set[i] == 0:
                self.data[row][1] = '0'
            else:
                self.data[row][1] = str(self.data_set[i])
                self.data[row][2] = 'Fail'
            row += 1

        # 更新数据表颜色格式
        for i in range(5, 11):
            if int(self.data[i][1]) > 0:
                self.style.add("TEXTCOLOR", (2, i), (2, i), colors.red)
                self.style.add("TEXTCOLOR", (1, 13), (1, 13), colors.red)
                self.data[13][1] = 'Fail'


        self.data[13][1] = self.qualified

        # 判断路径是否有效
        if (self.report_path.split('/'))[len(self.report_path.split('/')) - 1] == '':
            self.report_path += '/'

        report = SimpleDocTemplate(self.report_path + f"{self.data[0][1]}.pdf")

        # 获取样式
        styles = getSampleStyleSheet()
        story = []
        # 标题文字
        title = Paragraph("PCB inspection report", styles["Title"])
        story.append(title)
        story.append(Spacer(1, 12))

        # 创建图片对象
        # 样本图片
        if img1_org is not None:
            img1 = Img(img1_org)
            img1.drawHeight = 4 * cm
            img1.drawWidth = 4 * cm
            self.data[1][1] = img1
        if img2_output is not None:
            # 结果图片
            img2 = Img(img2_output)
            img2.drawHeight = 4 * cm
            img2.drawWidth = 4 * cm
            self.data[2][1] = img2

        table = Table(self.data, colWidths=[4 * cm, 3 * cm, 6 * cm])
        table.setStyle(self.style)

        story.append(table)
        story.append(Spacer(0.1, 12))

        # 放置图片在下方
        img = Img("bd/Picture1.png", width=5 * cm, height=5 * cm)
        img_table = Table([["", img]], colWidths=[12 * cm, 5 * cm])
        img_table.setStyle(TableStyle([
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0, colors.white)
        ]))
        story.append(img_table)
        report.build(story)
        # 报告信息存储测试 （测试使用）
        if self.init.if_report_exists(id):
            self.init.update_report(self.data[0][1], id)
        else:
            self.init.report_register(self.data[0][1])
        return [self.data[0][1],self.data[14][1]]

    # 批量检测下下载检测报告 single-当前报告下载模式 mult-全部报告下载模式
    def batch_download_report(self, index_id = "None",mode = 'single'):
        if len(self.last_batch_data) == 0:
            print("No data !")
            return False

        tmp_index = 0
        if index_id != "None":
            tmp_index = int(eval(index_id))

        if mode == 'single':
            # 更新报告序列号
            self.data[0][1] = self.init.auto_generate_report_id()
            # 更新下载时间
            self.data[14][1] = str(self.init.auto_generate_time())
            # 更新产品序列号
            self.data[12][1] = self.last_batch_data[tmp_index]['product_id']
            self.read_result()
            # 新的数据导入和更新
            tmp_num = ast.literal_eval(self.last_batch_data[tmp_index]['defect_num'])
            i = 0
            for _ in range(5,11):
                if tmp_num[i] == ' ':
                    self.data[_][1] = '0'
                    self.data[_][2] = 'Pass'
                else:
                    self.data[_][1] = tmp_num[i]
                    self.data[_][2] = 'Fail'
                i+=1
            self.data[13][1] = self.last_batch_data[tmp_index]['final_result']
            # 更新数据表
            for i in range(5, 11):
                if int(self.data[i][1]) > 0:
                    self.style.add("TEXTCOLOR", (2, i), (2, i), colors.red)
                    self.data[13][1] = 'Fail'
                else:
                    self.style.add("TEXTCOLOR", (2, i), (2, i), colors.green)

            if self.data[13][1] == 'Pass':
                self.style.add("TEXTCOLOR", (1, 13), (1, 13), colors.green)
            else:
                self.style.add("TEXTCOLOR", (1, 13), (1, 13), colors.red)

            # 判断路径是否有效
            if (self.report_path.split('/'))[len(self.report_path.split('/')) - 1] != '':
                self.report_path += '/'

            report = SimpleDocTemplate(self.report_path + f"{self.data[0][1]}.pdf")

            # 获取样式
            styles = getSampleStyleSheet()
            story = []
            # 标题文字
            title = Paragraph("PCB inspection report", styles["Title"])
            story.append(title)
            story.append(Spacer(1, 12))

            # 创建图片对象
            # 样本图片
            img1 = Img(self.last_batch_data[tmp_index]['org_address'])
            img1.drawHeight = 4 * cm
            img1.drawWidth = 4 * cm
            self.data[1][1] = img1
            # 结果图片
            img2 = Img(self.last_batch_data[tmp_index]['res_address'])
            img2.drawHeight = 4 * cm
            img2.drawWidth = 4 * cm
            self.data[2][1] = img2

            table = Table(self.data, colWidths=[4 * cm, 3 * cm, 6 * cm])
            table.setStyle(self.style)

            story.append(table)
            story.append(Spacer(0.1, 12))
                # 放置图片在下方
            img = Img("bd/Picture1.png", width=5 * cm, height=5 * cm)
            img_table = Table([["", img]], colWidths=[12 * cm, 5 * cm])
            img_table.setStyle(TableStyle([
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 0, colors.white)
                ]))
            story.append(img_table)
            report.build(story)
                # 报告信息存储测试 （测试使用）
            if self.init.if_report_exists(self.last_batch_data[tmp_index]['product_id']):
                self.init.update_report(self.data[0][1], self.last_batch_data[tmp_index]['product_id'])
            else:
                self.init.report_register(self.data[0][1])
        else:
            for _ in range(len(self.last_batch_data)):
                # 更新报告序列号
                self.data[0][1] = self.init.auto_generate_report_id()
                # 更新下载时间
                self.data[14][1] = str(self.init.auto_generate_time())
                # 更新产品序列号
                self.data[12][1] = self.last_batch_data[_]['product_id']
                print(_)
                self.data[13][1] = self.last_batch_data[_]['final_result']
                self.read_result()
                # 新的数据导入和更新
                tmp_num = ast.literal_eval(self.last_batch_data[_]['defect_num'])

                i = 0
                for j in range(5, 11):
                    if tmp_num[i] == ' ':
                        self.data[j][1] = '0'
                        self.data[j][2] = 'Pass'
                    else:
                        self.data[j][1] = tmp_num[i]
                        self.data[j][2] = 'Fail'
                    i += 1

                # 更新数据表
                for i in range(5, 11):
                    if int(self.data[i][1]) > 0:
                        self.style.add("TEXTCOLOR", (2, i), (2, i), colors.red)
                        self.data[13][1] = 'Fail'
                    else:
                        self.style.add("TEXTCOLOR", (2, i), (2, i), colors.green)

                if self.data[13][1] == 'Pass':
                    self.style.add("TEXTCOLOR", (1, 13), (1, 13), colors.green)
                else:
                    self.style.add("TEXTCOLOR", (1, 13), (1, 13), colors.red)

                # 判断路径是否有效
                if (self.report_path.split('/'))[len(self.report_path.split('/')) - 1] != '':
                    self.report_path += '/'

                report = SimpleDocTemplate(self.report_path + f"{self.data[0][1]}.pdf")

                # 获取样式
                styles = getSampleStyleSheet()
                story = []
                # 标题文字
                title = Paragraph("PCB Detection Report", styles["Title"])
                story.append(title)
                story.append(Spacer(1, 12))

                # 创建图片对象
                # 样本图片
                img1 = Img(self.last_batch_data[_]['org_address'])
                img1.drawHeight = 4 * cm
                img1.drawWidth = 4 * cm
                self.data[1][1] = img1
                # 结果图片
                img2 = Img(self.last_batch_data[_]['res_address'])
                img2.drawHeight = 4 * cm
                img2.drawWidth = 4 * cm
                self.data[2][1] = img2

                table = Table(self.data, colWidths=[4 * cm, 3 * cm, 6 * cm])
                table.setStyle(self.style)

                story.append(table)
                story.append(Spacer(0.1, 12))
                # 放置图片在下方
                img = Img("bd/Picture1.png", width=5 * cm, height=5 * cm)
                img_table = Table([["", img]], colWidths=[12 * cm, 5 * cm])
                img_table.setStyle(TableStyle([
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 0, colors.white)
                ]))
                story.append(img_table)
                report.build(story)
                # 报告信息存储测试 （测试使用）
                if self.init.if_report_exists(self.last_batch_data[_]['product_id']):
                    self.init.update_report(self.data[0][1], self.last_batch_data[_]['product_id'])
                else:
                    self.init.report_register(self.data[0][1], product_id=self.last_batch_data[_]['product_id'])

        return True

    # 下载检测报告
    def download_report(self, product_id = ""):
        # 更新报告序列号
        self.data[0][1] = self.init.auto_generate_report_id()
        # 更新下载时间
        self.data[14][1] = str(self.init.auto_generate_time())
        # 更新产品序列号
        self.data[12][1] = product_id
        self.read_result()


        # 判断路径是否有效
        if (self.report_path.split('/'))[len(self.report_path.split('/')) - 1] != '':
            self.report_path += '/'

        report = SimpleDocTemplate(self.report_path + f"{self.data[0][1]}.pdf")

        # 获取样式
        styles = getSampleStyleSheet()
        story = []
        # 标题文字
        title = Paragraph("PCB Detection Report", styles["Title"])
        story.append(title)
        story.append(Spacer(1, 12))

        # 创建图片对象
        # 样本图片
        img1 = Img(self.imgs_address)
        img1.drawHeight = 4 * cm
        img1.drawWidth = 4 * cm
        self.data[1][1] = img1
        # 结果图片
        img2 = Img(
            self.result_save_address + self.save_filename + "/" + self.imgs_name + "." + "jpg")
        img2.drawHeight = 4 * cm
        img2.drawWidth = 4 * cm
        self.data[2][1] = img2

        table = Table(self.data, colWidths=[4 * cm, 3 * cm, 6 * cm])
        table.setStyle(self.style)

        story.append(table)
        story.append(Spacer(0.1, 12))
        # 放置图片在下方
        img = Img("bd/Picture1.png", width=5 * cm, height=5 * cm)
        img_table = Table([["", img]], colWidths=[12 * cm, 5 * cm])
        img_table.setStyle(TableStyle([
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0, colors.white)
        ]))
        story.append(img_table)
        report.build(story)
        # 报告信息存储测试 （测试使用）
        if self.init.if_report_exists(product_id):
            self.init.update_report(self.data[0][1],product_id)
        else:
            self.init.report_register(self.data[0][1])


    # 生成检测数据
    def auto_create_data(self, defect_reason):
        # 判断有没有结果
        if len(self.result) > 0:
            # 更新表数据
            for i in range(len(self.result)):
                for j in range(5,11):
                    pro_result = self.result[i]
                    if len(self.result[i].split('_')) > 1:
                        pro_result = (self.result[i].split('_'))[0] + " " + (self.result[i].split('_'))[1]
                    if pro_result == self.data[j][0].lower():
                        self.data[j][1] = str(int(self.data[j][1]) + 1)
                        self.data[j][2] =  "Fail"
                        self.data[13][1] = self.qualified
                        self.style.add("TEXTCOLOR", (1, 13), (1, 13), colors.red)

        else:
            # 没有结果， 所有字体为绿色
            self.style.add("TEXTCOLOR", (2, 5), (2, 5), colors.green)
            self.style.add("TEXTCOLOR", (2, 6), (2, 6), colors.green)
            self.style.add("TEXTCOLOR", (2, 7), (2, 7), colors.green)
            self.style.add("TEXTCOLOR", (2, 8), (2, 8), colors.green)
            self.style.add("TEXTCOLOR", (2, 9), (2, 9), colors.green)
            self.style.add("TEXTCOLOR", (2, 10), (2, 10), colors.green)
            self.style.add("TEXTCOLOR", (1, 13), (1, 13), colors.green)
            self.data[13][1] = 'Pass'

        # 更新数据表
        for i in range(5,11):
            if int(self.data[i][1]) > 0:
                self.style.add("TEXTCOLOR", (2, i), (2, i), colors.red)
                self.data[13][1] = 'Fail'
            else:
                self.style.add("TEXTCOLOR", (2, i), (2, i), colors.green)



    #实时检测模块
    def real_time_detect(self):
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        cap = cv2.VideoCapture(0)
        # 设置编码格式
        video_format = cv2.VideoWriter_fourcc(*'mp4v')
        # 创建VideoWriter对象
        out = cv2.VideoWriter('output.mp4',video_format,20.0,(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
        skip_frames = 5
        frame_count = 0
        model = YOLO(self.best_weights).to(device=device)
        print(f"current device: {device}")
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            frame_count += 1
            if frame_count % skip_frames != 0:
                continue
            # 缩小图像以加快推理速度
            scale_percent = 80
            width = int(frame.shape[1] * scale_percent / 100)
            height = int(frame.shape[0] * scale_percent / 100)
            resized_frame = cv2.resize(frame, (width, height))
            # 模型推理
            results = model(resized_frame)
            # 绘制检测结果
            annotated_frame = results[0].plot()
            # 显示结果
            cv2.imshow("PCB real time detector", annotated_frame)
            # 写入文件
            out.write(frame)
                # 按下 'e' 键退出
            if cv2.waitKey(1) & 0xFF == ord('e'):
                break

        cap.release()
        cv2.destroyAllWindows()

    # 数据导入文件中
    def record_speed(self, pp, infer, post):
        try:
            filepath = "C:/Users/Bao/Desktop/tmp.txt"
            with open(filepath, 'a', encoding='utf-8') as file:  # 使用 'a' 追加模式
                file.write(f"{pp:.1f}ms,{infer:.1f}ms,{post:.1f}ms\n")
            print(f"recorded success: {filepath}")
        except Exception as e:
            print(f"recorded fail: {e}")

    # 批量检测
    def batch_run_model(self):
        # 获取图片感知hash
        img_hash = imagehash.phash(Image.open(self.imgs_address))
        if self.init.if_product_exists(str(img_hash)):
            self.init.product_code = self.init.get_product_code_by_hash(str(img_hash))
            self.data[12][1] = self.init.product_code
        else:
            # 更新产品序列号
            self.data[12][1] = self.init.auto_generate_code()

        for _ in range(5,11):
            self.data[_][1] = '0'

        if self.if_imgs_address_valid():
            # 删除文件夹 （测试使用）
            # self.remove_dir()
            # 识别后保存文件 在 .. runs/detect/ 下面
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            result_output = self.model.predict(self.imgs_address, project=self.result_save_address, save=True, save_conf=True,
                                               save_txt=True, name=self.save_filename,device = device)
            print(f"current device: {device}")
            if len(self.result) > 0:
                self.result.clear()

            # 获取模型内所有的标签名称
            all_names = self.model.model.names
            # 遍历检测结果
            for i in result_output:
                boxes = i.boxes
                for box in boxes:
                    id = int(box.cls)
                    self.result.append(all_names[id])

            # 测试代码
            # 记录数据
            if isinstance(result_output, list) and len(result_output) > 0:
                for result in result_output:
                    if hasattr(result, 'speed'):
                        speed = result.speed
                        if isinstance(speed, dict):
                            preprocess = speed.get('preprocess', 0)
                            inference = speed.get('inference', 0)
                            postprocess = speed.get('postprocess', 0)
                            self.record_speed(preprocess, inference, postprocess)
                            break


            print(self.result)
            self.spilt_imgs_infor()
            # 识别检测结果
            self.read_result()

            # 生成报告 (测试使用)
            self.auto_create_data(self.result)

            # 报告数据处理和转换
            data_count = []
            data_reason = []
            for i in range(5, 11):
                if int(self.data[i][1]) > 0:
                    data_count.append(self.data[i][1])
                    data_reason.append(self.data[i][0])
                else:
                    data_count.append(" ")
                    data_reason.append(" ")

            output_address = self.result_save_address + self.save_filename + "/" + self.imgs_name + "." + "jpg"
            print(output_address)


            img_s = Image.open(self.imgs_address)
            size = str(img_s.width) + "x" + str(img_s.height)

            tmp = {"product_id": self.data[12][1],"img_size":size, "img_name": self.imgs_name,
                   "org_address": self.imgs_address, "res_address": output_address,
                   "final_result": self.qualified, "defect_num": str(data_count), "img_type": self.imgs_type,
                   "defect_infor": str(data_reason),"hash":str(img_hash)}
            # 如果产品信息存在，则更新数据库
            if self.init.if_product_exists(str(img_hash)):
                self.init.update_product_by_hash(str(img_hash), self.imgs_address, output_address, self.imgs_name,
                                                 self.qualified, str(data_count), str(data_reason))

                self.last_batch_data.append(tmp)
            else:

                print(self.imgs_name)
                # 上传结果到数据库
                self.init.pcb_register(self.data[12][1], self.imgs_name, self.imgs_address, output_address,
                                       self.qualified, str(data_count), self.imgs_type, str(data_reason))

                self.last_batch_data.append(tmp)
        return "None"

    # 运行模型
    def run_model(self,model = 0):
        # 更新产品序列号
        self.data[12][1] = self.init.auto_generate_code()

        if model == 1:
            self.real_time_detect()
            return True
        else:
            if self.if_imgs_address_valid():
                # 删除文件夹 （测试使用）
                #self.remove_dir()
                # 识别后保存文件 在 .. runs/detect/ 下面
                device = 'cuda' if torch.cuda.is_available() else 'cpu'
                result_output = self.model.predict(self.imgs_address, project=self.result_save_address ,save=True, save_conf=True, save_txt=True, name=self.save_filename,device=device)
                print(f"current device: {device}")
                if len(self.result) > 0:
                    self.result.clear()
                # 获取模型内所有的标签名称
                all_names = self.model.model.names
                # 遍历检测结果
                for i in result_output:
                    boxes = i.boxes
                    for box in boxes:
                        id = int(box.cls)
                        self.result.append(all_names[id])

                print(self.result)
                self.spilt_imgs_infor()
                # 识别检测结果
                self.read_result()
                # 生成报告 (测试使用)
                self.auto_create_data(self.result)
                # 报告数据处理和转换
                data_count = []
                data_reason = []
                for i in range(5,11):
                    if int(self.data[i][1]) > 0:
                        data_count.append(self.data[i][1])
                        data_reason.append(self.data[i][0])
                    else:
                        data_count.append(" ")
                        data_reason.append(" ")
                output_address = self.result_save_address + self.save_filename + "/" + self.imgs_name + "." + "jpg"
                print(output_address)

                # 获取图片感知hash
                img_hash = imagehash.phash(Image.open(self.imgs_address))
                # 如果产品信息存在，则更新数据库
                if self.init.if_product_exists(str(img_hash)):
                    self.init.update_product_by_hash(str(img_hash),self.imgs_address,output_address,self.imgs_name,self.qualified,str(data_count),str(data_reason))
                    self.init.product_code = self.init.get_product_code_by_hash(str(img_hash))
                else:
                    # 上传结果到数据库
                    self.init.pcb_register(self.data[12][1],self.imgs_name, self.imgs_address,output_address, self.qualified, str(data_count), self.imgs_type, str(data_reason))
                return output_address
            return "None"

