# 利用已有参数模型输出结果

# 1. 导入库
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

class Dataloader:
    def __init__(self, source= "eval_data/csv_img/temp.jpg", transform=None):
        self.transform = transform
        self.path = [source]
    
    def __getitem__(self, item):
        """
        @brief: 获取指定索引的图片路径
        @param item: 索引
        @return: 图片路径
        """
        transform =  transforms.Compose([
                        transforms.ToTensor(), 
                    ]) 
        img_file = self.path[item]
        img = Image.open(img_file)
        if self.transform:
            img = self.transform(img)
        else:
            img = transform(img)

        return img
    
    def __len__(self):
        return 1

def eval( img_path='eval_data/csv_img/temp.jpg'):
    """
    @brief: 评估函数
    @param model: 模型
    @param img_path: 图片路径
    @return: None
    """
    # 检查是否有可用的GPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 加载预训练模型
    model = DACN(num_classes=3)
    model.load_state_dict(torch.load('best_model.pth', map_location=device))
    model.to(device)
    # 设置模型为评估模式
    model.eval()
    
    # 定义数据预处理
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    
    # 加载图片
    dataset = Dataloader(img_path)
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=1, shuffle=False)
    
    # 遍历数据集进行预测
    for images in dataloader:
        images = images.to(device)
        outputs,outpspa,outpcga,afespa,afecga = model(images)
        _, predicted = torch.max(outputs.data, 1)
        print(f'Predicted class: {predicted.item()}')

if __name__ == "__main__":
    #打印当前路径
    # print("Current working directory:", os.getcwd())
    
    eval_img = os.path.join(eval_csv_img_path, 'temp.jpg')
    # 评估模型
    eval(img_path=eval_img)

