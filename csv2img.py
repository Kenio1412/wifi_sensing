# 将csv 转化为 img(jpg文件)

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from PIL import Image

# sniff_time格式的时间戳转换为时间戳格式的时间
# 例如：sniff_time = '2025-03-18 10:04:34.002879'，转换为timestamp = 1679118274.002879
def sniff_time_to_timestamp(sniff_time):
    """
    @brief: 将sniff_time转换为时间戳
    @param sniff_time: sniff_time格式的时间
    @return: 时间戳格式的时间
    """
    return pd.to_datetime(sniff_time).timestamp()

class CSV2Img:
    def __init__(self):
        self.df = None
        self.time_interval = None
        self.time_column = None
        self.count_column = None
        self.length = None
        self.count_column = 'ra'
        self.time_column = 'timestamp'
        self.df = None
    
    def read_csv(self, path = 'csv/1_1.csv'):
        """
        @brief: 读取csv文件
        @param path: csv文件路径，默认为'csv/1_1_packets.csv'
        @return: None
        """
        self.df = pd.read_csv(path)
        self.length = 'length'
        self.df[self.time_column] = self.df[self.time_column].apply(sniff_time_to_timestamp)
        self.df[self.length] = self.df[self.length].astype(int)
        self.df = self.df.sort_values(by=self.time_column)
    
    def csv_to_img(self, source='csv_group/1_1.csv',output='csv_img/1_1.jpg'):
        """
        @brief: 将csv文件转换为图片
        @return: None
        """
        self.read_csv(source)
        # 绘制time_column-length曲线图
        plt.figure(figsize=(10, 5))
        plt.plot(self.df[self.time_column], self.df[self.length])
        plt.savefig(output)
        plt.close()
        # print(f"Image saved to {output}")
    
    def batch_csv_to_img(self, source_dir='csv_group', output_dir='csv_img'):
        """
        @brief: 批量将csv文件转换为图片
        @return: None
        """
        if not os.path.exists(output_dir):
            raise ValueError(f"Output directory {output_dir} does not exist.")
        if not os.path.exists(source_dir):
            raise ValueError(f"Source directory {source_dir} does not exist.")
        for file in tqdm(os.listdir(source_dir), desc="Processing", unit="files"):
            if file.endswith('.csv') and file != 'output.csv':
                self.csv_to_img(os.path.join(source_dir, file), os.path.join(output_dir, file.replace('.csv', '.jpg')))

    def read_img(self, path='csv_img/1_1.jpg'):
        """
        @brief: 读取图片
        @param path: 图片路径，默认为'csv_img/1_1.jpg'
        @return: None
        """
        img = Image.open(path)
        print(f"Image size: {img.size}")

if __name__ == '__main__':
    csv2img = CSV2Img()
    csv2img.batch_csv_to_img(source_dir='csv_group',output_dir='csv_img')
    # csv2img.read_img(path='csv_img/1_1.jpg')
        
        