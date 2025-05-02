# 将csv文件中的数据进行处理，将数据进行分组，统计每个时间段内的数据包数量，并将结果保存到新的csv文件中
# 统计每个时间段内的数据包数量，并将结果保存到新的csv文件中

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from tqdm import tqdm

# sniff_time格式的时间戳转换为时间戳格式的时间
# 例如：sniff_time = '2025-03-18 10:04:34.002879'，转换为timestamp = 1679118274.002879
def sniff_time_to_timestamp(sniff_time):
    """
    @brief: 将sniff_time转换为时间戳
    @param sniff_time: sniff_time格式的时间
    @return: 时间戳格式的时间
    """
    return pd.to_datetime(sniff_time).timestamp()


class CSV_Solver:
    def __init__(self):
        self.df = None
        self.time_interval = None
        self.time_column = None
        self.count_column = None
        self.length = None
        self.count_column = 'ra'
    
    def read_csv(self, path = 'csv/1_1.csv'):
        """
        @brief: 读取csv文件
        @param path: csv文件路径，默认为'csv/1_1_packets.csv'
        @return: None
        """
        self.df = pd.read_csv(path)
        self.time_column = 'timestamp'
        self.length = 'length'
        self.df[self.time_column] = self.df[self.time_column].apply(sniff_time_to_timestamp)
        self.df[self.length] = self.df[self.length].astype(int)
        self.df = self.df.sort_values(by=self.time_column)
    
    def group_by_time(self, time_interval=1,path='csv_group/1_1_packets_grouped.csv'):
        """
        @brief: 按照时间间隔分组
        @param time_interval: 时间间隔，单位为秒
        @return: None
        """
        if self.df is None:
            self.read_csv()
        self.time_interval = time_interval
        self.df['time_group'] = (self.df[self.time_column] // self.time_interval).astype(int)
        # 统计每个时间段内的数据包数量和总长度
        # self.df = self.df.groupby('time_group').agg({self.count_column: 'count', 'length': 'sum'}).reset_index()
        self.df = self.df.groupby('time_group').agg({self.count_column:'count',self.length: 'sum'}).reset_index()
        self.df[self.time_column] = self.df['time_group'] * self.time_interval
        self.df = self.df.drop(columns=['time_group'])
        # 将时间戳转换为时间格式
        self.df[self.time_column] = pd.to_datetime(self.df[self.time_column], unit='s')
        self.df = self.df.sort_values(by=self.time_column)
        # 修改列名
        self.df.rename(columns={self.count_column: 'count', self.length: 'length'}, inplace=True)
        # 增加一列，表示平均长度
        self.df['avg_length'] = self.df['length'] / self.df['count']
        # 增加一列，表示时间间隔
        self.df['time_interval'] = self.time_interval
        # 保存分组后的数据到csv文件
        self.df.to_csv(path, index=False)
        print(f"Grouped data saved to {path}")
    
    def batch_group_by_time(self, source_dir=None, output_dir=None, time_interval=1):
        """
        @brief: 批量处理csv文件，按照时间间隔分组
        @param source_dir: csv文件目录，默认为'csv'
        @param output_dir: 输出目录，默认为'csv_group'
        @param time_interval: 时间间隔，单位为秒
        @return: None
        """
        if not source_dir:
            source_dir = 'csv'
        if not output_dir:
            output_dir = 'csv_group'

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for file in tqdm(os.listdir(source_dir), desc="Processing", unit="files"):
            if file.endswith('.csv'):
                self.read_csv(os.path.join(source_dir, file))
                self.group_by_time(time_interval, os.path.join(output_dir, file))
        

if __name__ == "__main__":
    # 测试代码
    csv_solver = CSV_Solver()
    csv_solver.read_csv('csv/1_1.csv')
    csv_solver.batch_group_by_time(source_dir='csv', output_dir='csv_group', time_interval=1)
