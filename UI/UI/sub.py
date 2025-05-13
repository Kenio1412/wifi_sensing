from sub_ui import Ui_Sub

from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import QCoreApplication, QRect , QThread , Slot, Signal

from eval import eval_csi, eval_pkt
from eval import CSI_Process, PKT_Process
import paramiko
import os
import asyncio
import time
import config
from auto_connect.connect import connect, prepare_environment
import threading

class DataThread(QThread):
    result_ready = Signal(str)
    message_ready = Signal(str)

    def __init__(self):
        super().__init__()
        self.csi_filename = 'csi.pcap'
        self.pkt_filename = 'pkt.pcap'
        self.running = True
        self.target_mac = config.Mac
        self.csi_conn, self.pkt_conn = connect()

    
    def prepare_environment(self):
        self.message_ready.emit("开始准备环境")
        prepare_environment(self.csi_conn, self.pkt_conn)
        self.message_ready.emit("准备环境完成")

    def get_result(self, csi_label, pkt_label):
        if csi_label == 0 and pkt_label == 0:
            return 0
        elif csi_label == 0 and pkt_label == 1:
            return 1
        elif csi_label == 0 and pkt_label == 2:
            return 4
        elif csi_label == 2 and pkt_label == 0:
            return 3
        else:
            return 2
    def run(self, data_path=config.local_path):
        self.running = True
        asyncio.set_event_loop(asyncio.new_event_loop())

        while self.running:
            self.message_ready.emit("处理中...")
            csi_thread = threading.Thread(
                target=self.csi_conn.start_capture,
                args=(10,)
            )
            pkt_thread = threading.Thread(
                target=self.pkt_conn.start_capture,
                args=(10,)
            )
            csi_thread.start()
            pkt_thread.start()

            csi_thread.join()
            pkt_thread.join()
            # # 本地路径保存地址
            csi_local_path = os.path.join(data_path, self.csi_filename)
            pkt_local_path = os.path.join(data_path, self.pkt_filename)
            self.csi_conn.transfer_file(local_path=csi_local_path) # 传输csi文件到本地
            self.pkt_conn.transfer_file()
            pi_pcap_path = config.pkt_pi_pcap_path + '/pkt.pcap'

            result_csi = eval_csi()
            csi_classes = ["人员静止（无明显肢体动作）", "人员小幅活动（如伸展、调整坐姿等）", "人员大幅移动（如行走、走动等）"]
            self.result_ready.emit(f"{csi_classes[result_csi]}")
            result_pkt = eval_pkt()
            pkt_classes = ["设备少流量", "中等流量，疑似看视频", "高流量，疑似下载或看直播"]
            self.result_ready.emit(f"{pkt_classes[result_pkt]}")
            result = self.get_result(result_csi, result_pkt)
            self.result_ready.emit("综合判断：")
            class_names = ['员工在偷懒', '员工在刷视频', '员工正常工作', '员工离开/员工回来', '员工在看直播/下载东西']
            self.result_ready.emit(f"{class_names[result]}")
    
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
            self.thread_data.wait()
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