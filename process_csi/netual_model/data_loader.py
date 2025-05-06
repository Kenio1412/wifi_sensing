import torch.utils.data as data
from PIL import Image
import os
import torchvision.transforms as transforms

class CSISubcarrierDataset(data.Dataset):
    def __init__(self, root_dir, subcarrier_idx, transform=None):
        """
        :param root_dir: 图像数据根目录
        :param subcarrier_idx: 指定加载哪一个子载波的数据(0-19)
        :param transform: 图像变换（如 ToTensor, Resize 等）
        """
        self.root_dir = root_dir
        self.subcarrier_idx = subcarrier_idx
        self.transform = transform if transform else transforms.ToTensor()
        self.jpg_file = []
        self.jpg_labels = []

        sub_dir = os.path.join(root_dir, f"subcarrier_{subcarrier_idx}")
        if not os.path.isdir(sub_dir):
            raise FileNotFoundError(f"目录不存在: {sub_dir}")
        # 预期文件名格式: <label>-<idx>-sub-<sub_id>.jpg
        for filename in os.listdir(sub_dir):
            if filename.endswith(".jpg"):
                parts = filename.split("-")
                label = int(parts[0]) - 1  # 假设类别是 1~5，转为 0~4
                if label == 0 or label == 1 or label == 4:
                    label = 0
                elif label == 3 :
                    lable = 2
                else:
                    label = 1
                self.jpg_file.append(os.path.join(sub_dir, filename))
                self.jpg_labels.append(label)

        self.count = len(self.jpg_file)

    def __getitem__(self, index):
        """
        @brief: 获取指定索引的图片路径
        @param item: 索引
        @return: 图片路径
        """
        img_path = self.jpg_file[index]
        # print(Image.open(img_path).size)
        label = self.jpg_labels[index]
        img = Image.open(img_path)
        # print(img.size)
        # img.show()

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