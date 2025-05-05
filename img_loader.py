import torch.utils.data as data
from PIL import Image
import os
import torchvision.transforms as transforms
#import cv2

class img_loader(data.Dataset):
    """
    @brief: 图片加载器
    @param source_dir: 图片目录，默认为'csv_img'
    @param output_dir: 输出目录，默认为'csv_group'
    """
    def __init__(self, source_dir='csv_img', transform=None):
        self.transform = transform
        self.source_dir = source_dir
        self.img_files = []
        self.img_lable = []
        self.count = 0
        for file in os.listdir(source_dir):
            if file.endswith('.jpg'):
                self.img_files.append(os.path.join(source_dir, file))
                self.img_lable.append(int(file.split('_')[0]) - 1)
                self.count += 1

    def __getitem__(self, item):
        """
        @brief: 获取指定索引的图片路径
        @param item: 索引
        @return: 图片路径
        """
        transform =  transforms.Compose([
                                    transforms.ToTensor(), 
                                    ]) 
        img_file = self.img_files[item]
        img = Image.open(img_file)
        label = self.img_lable[item]
        if label == 0 or label == 3 or label == 2:
            label = 0
        elif label == 1:
            label = 1
        elif label == 4:
            label = 2
        
        
        if self.transform:
            img = self.transform(img)
        else:
            img = transform(img)

        return img, label

    def __len__(self):
        """
        @brief: 获取图片数量
        @return: 图片数量
        """
        return self.count