import torch
from torchvision import transforms
from torch.utils.data import DataLoader
from model import DACN
from fusion_loader import test_pkt_loader, test_csi_loader
from PIL import Image
from torch.utils.data import Subset
import os
import re

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def extract_idx(path):
    name = os.path.basename(path)
    match = re.search(r'-(\d+)', name)
    return int(match.group(1)) if match else -1

def get_label(pkt_label, csi_label):
    if csi_label == 0 and pkt_label == 0:
        return 0
    elif csi_label == 0 and pkt_label == 1:
        return 1
    elif csi_label == 0 and pkt_label == 2:
        return 4
    elif csi_label == 2 and pkt_label == 0:
        return 3
    else:
        return 2

def main():
    pkt_dir = r'G:\Coding\wifi_sensing\pkt_img'
    csi_dir = r'G:\Coding\wifi_sensing\csi_img'
    model_pkt_path = r'G:\Coding\wifi_sensing\netual_model\pkt_model.pth'
    model_csi_path = r'G:\Coding\wifi_sensing\netual_model\csi_model.pth'
    transform = transforms.ToTensor()
    pkt_dataset = test_pkt_loader(pkt_dir, transform)
    csi_dataset = test_csi_loader(csi_dir, transform)

    pkt_dict = {os.path.basename(path): label for path, label, img in pkt_dataset}
    csi_dict = {os.path.basename(path): label for path, label, img in csi_dataset}
    shared_keys = sorted(set(pkt_dict.keys()) & set(csi_dict.keys()))
    label_mapping = {} 
    for fname in shared_keys:
        pkt_label = pkt_dict.get(fname, -1)
        csi_label = csi_dict.get(fname, -1)
        true_label = get_label(pkt_label, csi_label)
        label_mapping[fname] = true_label

    model_pkt = DACN(num_classes=3).to(device)
    model_csi = DACN(num_classes=3).to(device)
    model_pkt.load_state_dict(torch.load(model_pkt_path))
    model_csi.load_state_dict(torch.load(model_csi_path))
    model_pkt.eval()
    model_csi.eval()
    correct = 0
    total = len(shared_keys)
    with torch.no_grad():
        for idx in shared_keys:
            pkt_img_path = os.path.join(pkt_dir, idx)
            csi_img_path = os.path.join(csi_dir, idx)

            pkt_img = Image.open(pkt_img_path).convert('RGB')
            csi_img = Image.open(csi_img_path).convert('RGB')

            pkt_img = transform(pkt_img).unsqueeze(0).to(device)
            csi_img = transform(csi_img).unsqueeze(0).to(device)

            pkt_out = model_pkt(pkt_img)[0]
            csi_out = model_csi(csi_img)[0]

            pkt_pred = torch.argmax(pkt_out, dim=1).item()
            csi_pred = torch.argmax(csi_out, dim=1).item()
            
            true_label = label_mapping[idx]
            fused = get_label(pkt_pred, csi_pred)

            if fused == true_label:
                correct += 1
    acc = 100. * correct / total
    print(f"\n融合准确率：{acc:.2f}%  （正确: {correct} / 总数: {total}）")

if __name__ == '__main__':
    main()

