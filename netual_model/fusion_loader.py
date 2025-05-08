import torch.utils.data as data
from PIL import Image
import os
import torchvision.transforms as transforms

class test_pkt_loader(data.Dataset):
    """
    @brief: 图片加载器
    @param source_dir: 图片目录
    """
    def __init__(self, source_dir, transform):
        self.transform = transform
        self.source_dir = source_dir
        self.img_files = []
        self.img_labels = []
        self.count = 0
        for file in os.listdir(source_dir):
            if file.endswith('.jpg'):
                try:
                    parts = file[:-4].split('-')
                    label = int(parts[0]) - 1
                    idx = int(parts[1])
                    if idx > 96:
                        path = os.path.join(source_dir, file)
                        self.img_files.append(path)
                        if label in [0, 2, 3]:
                            mapped_label = 0
                        elif label == 1:
                            mapped_label = 1
                        elif label == 4:
                            mapped_label = 2
                        self.img_labels.append(mapped_label)
                except:
                    continue


    def __getitem__(self, index):
        """
        @brief: 获取指定索引的图片路径
        @param item: 索引
        @return: 图片路径
        """
        img = Image.open(self.img_files[index]).convert('RGB')
        if self.transform:
            img = self.transform(img)
        img_path = self.img_files[index]
        label = self.img_labels[index]
        img = Image.open(img_path)
        img = self.transform(img)
        return img_path, label, img

    def __len__(self):
        """
        @brief: 获取图片数量
        @return: 图片数量
        """
        return self.count
    
class test_csi_loader(data.Dataset):
    def __init__(self, root_dir, transform=None):
        """
        :param root_dir: 图像数据根目录
        :param transform: 图像变换（如 ToTensor, Resize 等）
        """
        self.root_dir = root_dir
        self.transform = transform if transform else transforms.ToTensor()
        self.jpg_files = []
        self.jpg_labels = []
        self.count = 0
        if not os.path.isdir(root_dir):
            raise FileNotFoundError(f"目录不存在: {root_dir}")
        for filename in os.listdir(root_dir):
            if filename.endswith(".jpg"):
                try:
                    parts = filename[:-4].split('-')
                    label = int(parts[0]) - 1
                    idx = int(parts[1])
                    if idx > 96:
                        path = os.path.join(root_dir, filename)
                        if label in [0, 1, 4]:
                            mapped_label = 0
                        elif label == 2:
                            mapped_label = 1
                        elif label == 3:
                            mapped_label = 2
                        self.jpg_files.append(path)
                        self.jpg_labels.append(mapped_label)
                except:
                    continue
        self.count = len(self.jpg_files)

    def __getitem__(self, index):
        """
        @brief: 获取指定索引的图片路径
        @param item: 索引
        @return: 图片路径
        """
        img_path = self.jpg_files[index]
        label = self.jpg_labels[index]
        img = Image.open(img_path).convert('RGB')
        if self.transform:
            img = self.transform(img)
        return img_path, label, img

    def __len__(self):
        """
        @brief: 获取图片数量
        @return: 图片数量
        """
        return self.count
