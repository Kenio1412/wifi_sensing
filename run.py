import torch
import torch.nn as nn
import torch.nn.functional as F
from model import SeqClassifierVarLen
from csv_loader import CSVLoader
import os
from tensorboardX import SummaryWriter


def get_model(model_name, input_size, hidden_size, num_classes):
    if model_name == 'SeqClassifierVarLen':
        return SeqClassifierVarLen(input_size, hidden_size, num_classes)
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


def run(device):
    # 设置随机种子
    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)

    # 超参数设置
    input_size = 1  # 输入特征维度
    hidden_size = 128  # LSTM隐藏层大小
    num_classes = 2  # 分类数量
    learning_rate = 0.001  # 学习率
    num_epochs = 10  # 训练轮数

    # 模型、优化器、损失函数和学习率调度器的选择
    model_name = 'SeqClassifierVarLen'
    optimizer_name = 'adam'
    loss_name = 'cross_entropy'
    scheduler_name = 'step_lr'
    step_size = 5
    gamma = 0.1
    batch_size = 32

    # 创建模型、优化器、损失函数和学习率调度器
    model = get_model(model_name, input_size, hidden_size, num_classes).to(device)
    optimizer = get_optimizer(model, optimizer_name, learning_rate)
    loss_function = get_loss_function(loss_name)
    scheduler = get_scheduler(optimizer, scheduler_name, step_size, gamma)

    # 创建数据集和数据加载器
    dataset = CSVLoader(source_dir='csv_group')
    train_loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True,num_workers=4)
    test_loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=False,num_workers=4)

    net = model.to(device)

    writer = SummaryWriter(log_dir='logs')
    best_acc = 50.0
    global_train_acc = []
    global_test_acc = []
    print("Start training...")

    for epoch in range(num_epochs):
        print(f"Epoch {epoch + 1}/{num_epochs}")
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        for i, (inputs, labels,lengths) in enumerate(train_loader,0):
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs.unsqueeze(2), lengths=lengths)
            assert outputs.shape[0] == labels.shape[0], f"Output shape {outputs.shape} does not match label shape {labels.shape}"
            loss = loss_function(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        scheduler.step()
        acc = 100 * correct / total
        print(f"Epoch [{epoch + 1}/{num_epochs}], Loss: {running_loss / len(train_loader):.4f}, Accuracy: {acc:.2f}%")
        writer.add_scalar('Loss/train', running_loss / len(train_loader), epoch)
        writer.add_scalar('Accuracy/train', acc, epoch)
        global_train_acc.append(acc)

        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), 'best_model.pth')
            print(f"Model saved with accuracy: {best_acc:.2f}%")
    print("Training finished.")
    

if __name__ == "__main__":
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    run(device)
    