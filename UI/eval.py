import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
import torchvision.models as models
from model import DACN
from PIL import Image
import os
import numpy as np
from config import *
import warnings
import matplotlib.pyplot as plt
from csitool.read_pcap import NEXBeamformReader
from csitool.passband import lowpass
from csitool import csitools as csitools
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
import pyshark
from tqdm import tqdm
import pandas as pd
import config

warnings.filterwarnings("ignore", category=UserWarning)

class CSI_Process:
    def __init__(self, pcap_path, output_path):
        """
        @brief: input
        @return: None
        """
        self.pcap_path = pcap_path
        self.img_path = output_path

    def remove_data_with_high_variance(self, data):
        data = np.array(data)
        for i in range(len(data) - 2, -1, -1):
            variance = np.var(data[i:])
            if variance > 2:
                return data[0:i]
                break
        return data

    def process_csi(self):
        pcap_dir = self.pcap_path
        output_path = self.img_path
        file_name = pcap_dir
        my_reader = NEXBeamformReader()
        
        csi_data = my_reader.read_file(file_name, scaled=True)
        csi_matrix, no_frames, no_subcarriers = csitools.get_CSI(csi_data)
        csi_matrix_first = csi_matrix[:, :, 0, 0]
        csi_matrix_first[csi_matrix_first == -np.inf] = np.nan
        imp_mean = SimpleImputer(missing_values=np.nan, strategy='mean')
        csi_matrix_first = imp_mean.fit_transform(csi_matrix_first)
        csi_matrix_squeeze = np.squeeze(csi_matrix_first)
        csi_matrix_squeezed = np.transpose(csi_matrix_squeeze)
        if len(csi_matrix_squeezed[1]) < 100:
            print("数据长度不足100, 无法进行处理")
            return False
        
        for x in range(no_subcarriers - 1):
            csi_matrix_squeezed[x] = lowpass(csi_matrix_squeezed[x], 3, 50, 5)
        csi_matrix_squeezed = np.transpose(csi_matrix_squeezed)
        pca = PCA(n_components=3)
        csipca = pca.fit_transform(csi_matrix_squeezed)
        csipca = np.transpose(csipca)

        main_csi = csipca[0]
        main_csi += csipca[1]
        main_csi += csipca[2]
        x = csi_data.timestamps - csi_data.timestamps[0]
        csipca0 = self.remove_data_with_high_variance(main_csi)
        x = x[:len(csipca0)]
        plt.figure(figsize=(10, 6))
        plt.plot(x, csipca0, label='')

        plt.title("", fontsize=14)
        plt.xlabel("", fontsize=12)
        plt.ylabel("", fontsize=12)
        plt.legend(fontsize=12)
        plt.savefig(output_path)
        plt.close()
        print(f"Saved: {output_path}")
        return True

class PKT_Process:
    def __init__(self, time_interval=1, filter_mac=None):
        self.time_interval = time_interval
        self.filter_mac = filter_mac

    def sniff_time_to_timestamp(self, sniff_time):
        return pd.to_datetime(sniff_time).timestamp()

    def pcap_to_dataframe(self, pcap_path):
        cap = pyshark.FileCapture(pcap_path, use_json=True)
        packet_list = []

        for packet in tqdm(cap, desc=f"Reading {os.path.basename(pcap_path)}", unit="pkt"):
            try:
                ra = packet.wlan.ra
                if self.filter_mac and ra != self.filter_mac:
                    continue
                timestamp = self.sniff_time_to_timestamp(packet.sniff_time)
                length = int(packet.length)
                packet_list.append({'timestamp': timestamp, 'length': length})
            except AttributeError:
                continue
        cap.close()
        return pd.DataFrame(packet_list)

    def group_dataframe(self, df):
        if df.empty:
            return df
        df = df.sort_values(by='timestamp')
        df['time_group'] = (df['timestamp'] // self.time_interval).astype(int)
        grouped = df.groupby('time_group').agg({
            'length': ['count', 'sum']
        }).reset_index()
        grouped.columns = ['time_group', 'count', 'length']
        grouped['timestamp'] = pd.to_datetime(grouped['time_group'] * self.time_interval, unit='s')
        grouped['avg_length'] = grouped['length'] / grouped['count']
        return grouped

    def pcap_to_img(self, pcap_path, img_path):
        df = self.pcap_to_dataframe(pcap_path)
        grouped_df = self.group_dataframe(df)
        if grouped_df.empty:
            print(f"[WARN] No data to plot for {pcap_path}")
            return

        plt.figure(figsize=(10, 5))
        plt.plot(grouped_df['timestamp'], grouped_df['length'])
        plt.title(f"")
        plt.xlabel("")
        plt.ylabel("")
        plt.tight_layout()
        plt.savefig(img_path)
        plt.close()
        print(f"[DONE] Image saved to {img_path}")

def eval_csi(local_path = config.local_path):
    """
    @brief: 评估函数
    @param model: 模型
    @param img_path: 图片路径
    @return: None
    """
    output_path=os.path.join(local_path, 'csi.jpg')
    pcap_path=os.path.join(local_path, 'csi.pcap')
    csi_processor = CSI_Process(pcap_path, output_path)
    print(f"[DONE] Image saved to {output_path}")
    success = csi_processor.process_csi()
    if success:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = DACN(num_classes=3)
        model.load_state_dict(torch.load(r'F:\Coding\wifi_sensing\UI\model\csi_model.pth', map_location=device))
        model.to(device)
        model.eval()   
        transform = transforms.ToTensor()
        with torch.no_grad():
            csi_img = Image.open(output_path)
            csi_img = transform(csi_img).unsqueeze(0).to(device)
            csi_out = model(csi_img)[0]
            csi_pred = torch.argmax(csi_out, dim=1).item()
            print(f"[INFO] CSI Prediction: {csi_pred}")
            return csi_pred
    else:
        print(f"[!] 处理CSI数据失败，无法进行评估")
        return -1

def eval_pkt(local_path = config.local_path):
    """
    @brief: 评估函数
    @param model: 模型
    @param local_path: 图片路径
    @return: None
    """
    # 检查是否有可用的GPU
    output_path=os.path.join(local_path, 'pkt.jpg')
    pcap_path=os.path.join(local_path, 'pkt.pcap')
    pkt_processor = PKT_Process(time_interval=1, filter_mac="f0:57:a6:a6:b6:b6")
    pkt_processor.pcap_to_img(pcap_path, output_path)
    print(f"[DONE] Image saved to {output_path}")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = DACN(num_classes=3)
    model.load_state_dict(torch.load(r'F:\Coding\wifi_sensing\UI\model\pkt_model.pth', map_location=device))
    model.to(device)
    model.eval()
    transform = transforms.ToTensor()
    with torch.no_grad():
        pkt_img = Image.open(output_path)
        pkt_img = transform(pkt_img).unsqueeze(0).to(device)
        pkt_out = model(pkt_img)[0]
        pkt_pred = torch.argmax(pkt_out, dim=1).item()
        return pkt_pred