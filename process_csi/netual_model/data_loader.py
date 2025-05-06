import torch.utils.data as data
from PIL import Image
import os
import torchvision.transforms as transforms

class CSIDataset(data.Dataset):
    def __init__(self, root_dir, transform=None):
        """
        :param root_dir: 图像数据根目录
        :param transform: 图像变换（如 ToTensor, Resize 等）
        """
        self.root_dir = root_dir
        self.transform = transform if transform else transforms.ToTensor()
        self.jpg_file = []
        self.jpg_labels = []
        if not os.path.isdir(root_dir):
            raise FileNotFoundError(f"目录不存在: {root_dir}")
        for filename in os.listdir(root_dir):
            if filename.endswith(".jpg"):
                parts = filename.split("-")
                label = int(parts[0]) - 1  # 假设类别是 1~5，转为 0~4
                if label == 0 or label == 1 or label == 4:
                    label = 0
                elif label == 3 :
                    label = 2
                else:
                    label = 1
                self.jpg_file.append(os.path.join(root_dir, filename))
                self.jpg_labels.append(label)

        self.count = len(self.jpg_file)

    def __getitem__(self, index):
        """
        @brief: 获取指定索引的图片路径
        @param item: 索引
        @return: 图片路径
        """
        img_path = self.jpg_file[index]
        label = self.jpg_labels[index]
        img = Image.open(img_path)

        if self.transform:
            img = self.transform(img)
        return img, label

    def __len__(self):
        """
        @brief: 获取图片数量
        @return: 图片数量
        """
        return self.count
    
# if __name__ == "__main__":
#     path = r'G:\Coding\wifi_sensing\process_csi\PCA_output\subcarrier_0\1-1_sub_0.jpg'
#     print(Image.open(path).size)
#     img = Image.open(path).convert('RGB')
#     print(img.size)
#     img.show()