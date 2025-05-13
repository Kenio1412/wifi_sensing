import torch
import torch.nn as nn
import torch.nn.functional as F
from model import DACN
import os
from tensorboardX import SummaryWriter
import torchvision.transforms as transforms
from csi_loader import CSIDataset
import numpy as np
from torch.utils.data import Subset
import re


def get_model(model_name, input_size, hidden_size, num_classes):
    if model_name == 'DACN':
        return DACN(num_classes=num_classes)
    else:
        raise ValueError(f"Model {model_name} not found.")

def get_optimizer(model, optimizer_name, learning_rate):
    if optimizer_name == 'adam':
        return torch.optim.Adam(model.parameters(), lr=learning_rate)
    elif optimizer_name == 'sgd':
        return torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9)
    else:
        raise ValueError(f"Optimizer {optimizer_name} not found.")

def get_loss_function(loss_name):
    if loss_name == 'cross_entropy':
        return nn.CrossEntropyLoss()
    elif loss_name == 'mse':
        return nn.MSELoss()
    else:
        raise ValueError(f"Loss function {loss_name} not found.")

def get_scheduler(optimizer, scheduler_name, step_size, gamma):
    if scheduler_name == 'step_lr':
        return torch.optim.lr_scheduler.StepLR(optimizer, step_size=step_size, gamma=gamma)
    elif scheduler_name == 'multi_step_lr':
        return torch.optim.lr_scheduler.MultiStepLR(optimizer, milestones=[30, 80], gamma=0.1)
    else:
        raise ValueError(f"Scheduler {scheduler_name} not found.")


def run(device,type = 'seq'):
    # 设置随机种子
    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)

    # 超参数设置
    input_size = 3
    hidden_size = 512  # 卷积层输出大小

    num_classes = 3  # 分类数量
    learning_rate = 0.001  # 学习率
    num_epochs = 10  # 训练轮数

    model_name = 'DACN'
    optimizer_name = 'adam'
    loss_name = 'cross_entropy'
    scheduler_name = 'step_lr'
    step_size = 2
    gamma = 0.1
    batch_size = 16

    model = get_model(model_name, input_size, hidden_size, num_classes).to(device)
    optimizer = get_optimizer(model, optimizer_name, learning_rate)
    loss_function = get_loss_function(loss_name)
    scheduler = get_scheduler(optimizer, scheduler_name, step_size, gamma)
    with open(f"training_csi_log.txt", "w") as log_file:
        model = get_model(model_name, input_size, hidden_size, num_classes).to(device)
        optimizer = get_optimizer(model, optimizer_name, learning_rate)
        loss_function = get_loss_function(loss_name)
        scheduler = get_scheduler(optimizer, scheduler_name, step_size, gamma)
        dataset = CSIDataset(root_dir='F:\\Coding\\wifi_sensing\\csi_img', transform=None)
        # print(len(dataset))
        if len(dataset) == 0:
            print("数据集为空，请检查数据集路径和文件格式。")
            return
        train_indices = []
        test_indices = []

        for i, (file_path, _) in enumerate(zip(dataset.jpg_file, dataset.jpg_labels)):
            # 文件名形如<label>-<idx>.jpg
            filename = os.path.basename(file_path)
            match = re.search(r'-(\d+)', filename)  # 提取idx
            if match:
                idx = int(match.group(1))
                if idx <= 96:
                    train_indices.append(i)
                else:
                    test_indices.append(i)

        train_dataset = Subset(dataset, train_indices)
        test_dataset = Subset(dataset, test_indices)

        train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
        test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=4)
        net = model.to(device)


        writer = SummaryWriter('./logs_img')
        global_train_acc = []
        global_test_acc = []
        print("Start training...")
        best_acc = 50
        print(f"====== Start training======")
        log_file.write(f"====== Start training======\n")
        for epoch in range(0, num_epochs):
            print('\nEpoch: %d' % (epoch + 1))
            net.train()
            sum_loss = 0.0
            correct = 0.0
            total = 0.0
            for i, data in enumerate(train_loader, 0):

                length = len(train_loader)
                inputs, labels = data
                inputs, labels = inputs.to(device), labels.to(device)
                optimizer.zero_grad()
                outputs,outpspa,outpcga,afespa,afecga = net(inputs)
                loss = loss_function(outputs, labels)
                loss.backward()
                optimizer.step()

                sum_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += predicted.eq(labels.data).cpu().sum()
                print('[epoch:%d, iter:%d] Loss: %.03f | Acc: %.3f%% '
                    % (epoch + 1, (i + 1), sum_loss / (i + 1), 100. * correct / total))
                log_file.write('[epoch:%d, iter:%d] Loss: %.03f | Acc: %.3f%% \n'
                    % (epoch + 1, (i + 1), sum_loss / (i + 1), 100. * correct / total))
                writer.add_scalar('train_loss', sum_loss / (i + 1), epoch + 1)
                global_train_acc.append(100. * correct / total)

            print("Waiting Test!")
            with torch.no_grad():
                correct = 0
                total = 0
                for data in test_loader:
                    net.eval()
                    images, labels = data
                    images, labels = images.to(device), labels.to(device)
                    outputs,outpspa,outpcga,afespa,afecga = net(images)
                    _, predicted = torch.max(outputs.data, 1)
                    total += labels.size(0)
                    correct += (predicted == labels).sum()
                print('Test Acc：%.3f%%' % (100. * correct / total))
                log_file.write('Test Acc：%.3f%%' % (100. * correct / total))
                acc = 100. * correct / total

                if acc > best_acc:
                    best_acc = acc
                    torch.save(model.state_dict(), f'csi_model.pth')
                    log_file.write(f"Best model saved with acc: {best_acc:.2f}%\n")
                global_test_acc.append(acc)
            scheduler.step()
        log_file.write(f"Best Test Acc: {best_acc:.3f}%\n")
        print(f"Finished training , best acc: {best_acc:.2f}%")


if __name__ == "__main__":
    # device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    run(device, type='img')
    