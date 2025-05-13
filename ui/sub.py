from ui.sub_ui import Ui_Sub

from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import QCoreApplication, QRect , QThread , Slot, Signal

from conn.conn import Conn
from eval import eval
from eval_load import Eval_Loader
import config
import paramiko
import os
import asyncio
import time


class DataThread(QThread):
    result_ready = Signal(str)
    message_ready = Signal(str)

    def __init__(self):
        super().__init__()
        self.filename = '0'  # 文件名


        self.running = True
        # 在这里执行耗时的操作
        self.raspberry_pi_ip = config.raspberry_pi_ip
        self.username = config.username
        self.raspberry_pi_password = config.raspberry_pi_password

        self.target_mac = config.bobMac                      # 目标MAC地址
        self.eval_loader = Eval_Loader(filter= 'wlan.addr == {}'.format(self.target_mac))

        self.conn = Conn(self.raspberry_pi_ip, self.username, self.raspberry_pi_password)
        # self.prepare_environment() # 准备环境



    
    def prepare_environment(self):
        self.message_ready.emit("开始准备环境")
        self.conn.connect()
        self.conn.prepare_environment() # 准备环境
        self.conn.set_monitor_mode(config.channel) # 设置树莓派的信道
        self.message_ready.emit("准备环境完成")


    def run(self):
        self.running = True
        asyncio.set_event_loop(asyncio.new_event_loop())

        while self.running:
            self.message_ready.emit("处理中...")
            self.filename = str(int(self.filename) + 1)  # 文件名自增
            # 本地路径保存地址
            local_path = config.eval_pcap_path + '/' + self.filename + '.pcap'

            # 检查本地路径是否存在，若存在则删除
            if os.path.exists(local_path):
                os.remove(local_path)
                print("File removed successfully")
            else:
                print("File does not exist")

            # 树莓派抓包文件路径
            pi_pcap_path = config.pi_pcap_path + '/' + self.filename + '.pcap'


            pcap_path = config.eval_pcap_path  + '/' + self.filename + '.pcap' # 本机抓包文件路径
            csv_path = config.eval_csv_path + '/' + self.filename + '.csv'  # 本机csv文件路径
            group_path = config.eval_csv_group_path + '/' + self.filename + '.csv' # 本机分组后的csv文件路径
            img_path = config.eval_csv_img_path + '/' + self.filename + '.jpg'   # 本机图片文件路径

            

            # self.message_ready.emit("开始抓包")
            self.conn.start_capture(duration=config.capture_time,pcap_path=pi_pcap_path) # 开始抓包
            # self.message_ready.emit("抓包完成")
            # self.message_ready.emit("开始传输文件")
            self.conn.transfer_file(local_path=local_path) # 传输文件到本地
            # self.message_ready.emit("传输文件完成")
            self.eval_loader.pcap_to_img(pcap_path=pcap_path, csv_path=csv_path, group_path=group_path, img_path=img_path, target_mac=self.target_mac)
            # self.message_ready.emit("图片生成完成")
            result = eval(img_path=img_path)
            if result == 0:
                self.message_ready.emit("评估结果：少流量，正常！")
            elif result == 1:
                self.message_ready.emit("评估结果：中等流量，疑似看视频！")
            elif result == 2:
                self.message_ready.emit("评估结果：高流量，疑似下载或直播！")
            # self.message_ready.emit("评估完成")
            # self.result_ready.emit(result) 
    
    def stop(self):
        # 停止线程的逻辑
        self.running = False
        # if self.conn:
        #     self.conn.stop_capture()
        asyncio.get_event_loop().stop()
        
    
    def close(self):
        self.conn.disconnect()


class SubWindow(QDialog, Ui_Sub):
    def __init__(self):
        super(SubWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Raspberry Pi Data Collector - Sub Window")
        # self.setWindowIcon(QIcon("icon.png"))  # 设置窗口图标
        self.back_Button.clicked.connect(self.back_button_clicked)

        self.testButton.clicked.connect(self.test_button_clicked)

        self.thread_data = DataThread()
        self.thread_data.result_ready.connect(self.update_text_browser)
        self.thread_data.message_ready.connect(self.update_text_browser)

        self.is_env_ready = False
        self.text_Browser.append("点击start，开始准备环境，预计需要25秒钟")
    
    @Slot()
    def back_button_clicked(self):
        if self.thread_data.isRunning():
            self.text_Browser.append("停止线程")
            self.thread_data.stop()
            self.thread_data.wait()
        self.thread_data.close()
        self.close()


    @Slot()
    def test_button_clicked(self):
        if self.thread_data.isRunning():
            self.testButton.setText("Start")
            self.thread_data.stop()
            self.thread_data.wait()  # 等待线程结束
        else:
            if not self.is_env_ready:

                self.text_Browser.clear()
                # self.text_Browser.append("准备环境")
                self.thread_data.prepare_environment()
                # self.text_Browser.append("准备环境完成")
                self.is_env_ready = True
            self.thread_data.start()
            self.testButton.setText("Stop")
        

    @Slot(str)
    def update_text_browser(self, result):
        self.text_Browser.append(result)