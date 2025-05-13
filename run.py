import torch
import torch.nn as nn
import torch.nn.functional as F
from model import SeqClassifierVarLen , DACN
from csv_loader import CSVLoader
from img_loader import img_loader
import os
from tensorboardX import SummaryWriter
import torchvision.transforms as transforms
import config
from eval_load import Eval_Loader
from conn.conn import Conn
from eval import eval


def get_model(model_name, input_size, hidden_size, num_classes):
    if model_name == 'SeqClassifierVarLen':
        return SeqClassifierVarLen(input_size, hidden_size, num_classes)
    elif model_name == 'DACN':
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
    if type == 'seq':
        input_size = 1  # 输入特征维度
        hidden_size = 128*2  # LSTM隐藏层大小
    elif type == 'img':
        input_size = 3
        hidden_size = 512  # 卷积层输出大小

    num_classes = 3  # 分类数量
    learning_rate = 0.001  # 学习率
    num_epochs = 10  # 训练轮数

    # 模型、优化器、损失函数和学习率调度器的选择
    if type == 'seq':
        model_name = 'SeqClassifierVarLen'
    elif type == 'img':
        model_name = 'DACN'
    optimizer_name = 'adam'
    loss_name = 'cross_entropy'
    scheduler_name = 'step_lr'
    step_size = 2
    gamma = 0.1
    batch_size = 32

    # 创建模型、优化器、损失函数和学习率调度器
    model = get_model(model_name, input_size, hidden_size, num_classes).to(device)
    optimizer = get_optimizer(model, optimizer_name, learning_rate)
    loss_function = get_loss_function(loss_name)
    scheduler = get_scheduler(optimizer, scheduler_name, step_size, gamma)

    # 创建数据集和数据加载器
    if type == 'seq':
        dataset = CSVLoader(source_dir='csv_group')
    elif type == 'img':
        # transform = transforms.Compose([
        #     transforms.Resize((224, 224)),
        #     transforms.ToTensor(),
        #     transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        # ])
        dataset = img_loader(source_dir='csv_img')
    # 切分数据集
    train_size = int(0.8 * len(dataset))
    test_size = len(dataset) - train_size
    train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True,num_workers=4)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size, shuffle=False,num_workers=4)

    net = model.to(device)
    if type == 'seq':

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
                if type == 'seq':
                    outputs = model(inputs.unsqueeze(2), lengths=lengths)
                # assert outputs.shape[0] == labels.shape[0], f"Output shape {outputs.shape} does not match label shape {labels.shape}"
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

    elif type == 'img':
        writer = SummaryWriter('./logs_img')
        global_train_acc = []
        global_test_acc = []
        print("Start training...")
        best_acc = 50

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
                acc = 100. * correct / total

                if acc > best_acc:
                    best_acc = acc
                    torch.save(model.state_dict(), 'best_model.pth')
                    print(f"Model saved with accuracy: {best_acc:.2f}%")
                global_test_acc.append(acc)
            scheduler.step()
            # acc = 100 * correct / total
            # print(f"Epoch [{epoch + 1}/{num_epochs}], Loss: {sum_loss / len(train_loader):.4f}, Accuracy: {acc:.2f}%")
            # writer.add_scalar('Loss/train', sum_loss / len(train_loader), epoch)
            # writer.add_scalar('Accuracy/train', acc, epoch)
            # global_train_acc.append(acc)


        print("Training finished.")



def pi_run():
    raspberry_pi_ip = config.raspberry_pi_ip
    username = config.username
    raspberry_pi_password = config.raspberry_pi_password

    target_mac = config.bobMac                      # 目标MAC地址
    eval_loader = Eval_Loader(filter= 'wlan.addr == {}'.format(target_mac))

    conn = Conn(raspberry_pi_ip, username, raspberry_pi_password)

    conn.connect()
    # conn.prepare_environment() # 准备环境
    # conn.set_monitor_mode(config.channel) # 设置树莓派的信道



    filename = '5'
    for filename in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
        # 本地路径保存地址
        local_path = config.eval_pcap_path + '/' + filename + '.pcap'

        # 检查本地路径是否存在，若存在则删除
        if os.path.exists(local_path):
            os.remove(local_path)
            print("File removed successfully")
        else:
            print("File does not exist")

        # 树莓派抓包文件路径
        pi_pcap_path = config.pi_pcap_path + '/' + filename + '.pcap'


        pcap_path = config.eval_pcap_path  + '/' + filename + '.pcap' # 本机抓包文件路径
        csv_path = config.eval_csv_path + '/' + filename + '.csv'  # 本机csv文件路径
        group_path = config.eval_csv_group_path + '/' + filename + '.csv' # 本机分组后的csv文件路径
        img_path = config.eval_csv_img_path + '/' + filename + '.jpg'   # 本机图片文件路径

        


        conn.start_capture(duration=config.capture_time,pcap_path=pi_pcap_path) # 开始抓包
        conn.transfer_file(local_path=local_path) # 传输文件到本地

        eval_loader.pcap_to_img(pcap_path=pcap_path, csv_path=csv_path, group_path=group_path, img_path=img_path, target_mac=target_mac)

        eval(img_path=img_path)


    conn.disconnect() 

if __name__ == "__main__":
    # device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    # print(f"Using device: {device}")
    # run(device,type='img')

    pi_run()
    