from pcap_solver import PcapSolver
from csv_solver import CSV_Solver
from csv2img import CSV2Img
from img_loader import img_loader
import torch
import os
import pyshark
import time
from config import *

class Eval_Loader:
    def __init__(self,filePath=None,filter=None):
        
        self.pcap_solver = PcapSolver(filePath=filePath,filter=filter)
        self.csv_solver = CSV_Solver()
        self.csv2img = CSV2Img()
        self.img_loader = img_loader()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    def pcap_to_csv(self, pcap_path='eval_data/pcap/1_1.pcap', csv_path='eval_data/csv/1_1.csv',target_mac=None):
        """
        @brief: 将pcap文件转换为csv文件
        @param pcap_path: pcap文件路径
        @param csv_path: csv文件路径
        @return: None
        """
        # self.pcap_solver.read_pcap(pcap_path)
        self.pcap_solver.extract(pcap_path,csv_path,target_mac=target_mac)
    
    def csv_group(self, csv_path='eval/csv/1_1.csv', group_path='eval/csv_group/1_1_group.csv'):
        """
        @brief: 将csv文件分组
        @param csv_path: csv文件路径
        @param group_path: 分组后的csv文件路径
        @return: None
        """
        self.csv_solver.read_csv(csv_path)
        self.csv_solver.group_by_time(1, group_path)

    def csv_to_img(self, csv_path='eval/csv_group/1_1_group.csv', img_path='eval/csv_img/1_1_img.jpg'):
        """
        @brief: 将csv文件转换为图片
        @param csv_path: csv文件路径
        @param img_path: 图片文件路径
        @return: None
        """
        self.csv2img.csv_to_img(csv_path, img_path)
    
    def pcap_to_img(self, pcap_path='eval/pcap/1_1.pcap', csv_path='eval/csv/1_1.csv', group_path='eval/csv_group/1_1_group.csv', img_path='eval/csv_img/1_1_img.jpg',target_mac=None):
        """
        @brief: 将pcap文件转换为图片
        @param pcap_path: pcap文件路径
        @param csv_path: csv文件路径
        @param group_path: 分组后的csv文件路径
        @param img_path: 图片文件路径
        @return: None
        """
        
        self.pcap_to_csv(pcap_path, csv_path, target_mac=target_mac)
        self.csv_group(csv_path, group_path)
        self.csv_to_img(group_path, img_path)

if __name__ == "__main__":
    # # 打印当前路径
    # print("Current working directory:", os.getcwd())
    file_path = r'eval_data\pcap\pcap.pcap'
    # cap = pyshark.FileCapture(file_path)
    # print("Packet capture file loaded successfully.")
    
    pcap_path = eval_pcap_path + '/temp.pcap'
    csv_path = eval_csv_path + '/temp.csv'
    group_path = eval_csv_group_path + '/temp.csv'
    img_path = eval_csv_img_path + '/temp.jpg'
    target_mac = bobMac
    eval_loader = Eval_Loader(filter= 'wlan.addr == {}'.format(target_mac))

    eval_loader.pcap_to_csv(pcap_path=pcap_path, csv_path=csv_path, target_mac=target_mac)


