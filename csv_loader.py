import os
import pandas as pd
import torch.utils.data as data
import torch
import torchvision.transforms as transforms

source_dir = 'csv_group'

class CSVLoader(data.Dataset):
    """
    @brief: CSV文件加载器
    @param source_dir: csv文件目录，默认为'csv'
    @param output_dir: 输出目录，默认为'csv_group'
    @param time_interval: 时间间隔，单位为秒
    """
    def __init__(self, source_dir='csv_group',transform=None):
        self.transform = transform
        self.source_dir = source_dir
        self.csv_files = []
        self.csv_lable = []
        self.count = 0
        self.max_len = 30
        for file in os.listdir(source_dir):
            if file.endswith('.csv') and file != 'output.csv':
                self.csv_files.append(os.path.join(source_dir, file))
                self.csv_lable.append(int(file.split('_')[0]) - 1)
                self.count += 1
    
    def __getitem__(self, item):
        """
        @brief: 获取指定索引的csv文件路径
        @param item: 索引
        @return: csv文件路径
        """
        # transform = transforms.Compose([
        #     transforms.ToTensor(),
        #     # transforms.Normalize((0.5,), (0.5,))
        # ])
        csv_file = self.csv_files[item]
        df = pd.read_csv(csv_file)
        df = df['length'].to_numpy()
        len_df = len(df)
        # 长度填充
        if len_df < self.max_len:
            df = torch.nn.functional.pad(torch.from_numpy(df), (0, self.max_len - len_df), 'constant', 0)
        elif len_df > self.max_len:
            df = torch.from_numpy(df[:self.max_len])
        input = df.detach().clone()
        input = input.float()
        label = self.csv_lable[item]
        if label == 0 or label == 3 or label == 2:
            label = 0
        elif label == 1 :
            label = 1
        elif label == 4:
            label = 1
        len_df = len_df if len_df < self.max_len else self.max_len
        
        return input, label ,len_df
    
    def __len__(self):
        """
        @brief: 获取csv文件数量
        @return: csv文件数量
        """
        return self.count
    
if __name__ == "__main__":
    # 测试代码
    csv_loader = CSVLoader()
    print(csv_loader[0])
    print(csv_loader.__len__())
    # print(csv_loader.__getitem__(0))

        
    