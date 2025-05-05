import torch
import torch.nn.functional as F
import torch.nn as nn
import torchvision.models as models
import torch.optim as optim
import torchvision.transforms as transforms
from tensorboardX import SummaryWriter
from model1 import *
from da_att import SpatialGate, ChannelGate


class DACN(nn.Module):
    def __init__(self, num_classes=10):
        super(DACN, self).__init__()
        self.spa = SpatialGate()
        self.cga = ChannelGate(512)
        resnet = models.resnet18(pretrained=True)
        self.features = nn.Sequential(*list(resnet.children())[:-2])  
        self.avgpool = nn.AvgPool2d(7)
        self.fc = nn.Linear(512,6)
        self.fc2 = nn.Linear(4096,512)
        self.relu = nn.ReLU()
        
    def forward(self, x):       
        outspa, afspa = self.spa(x)
        out = self.features(outspa) 
        outcga, afcga = self.cga(out)
        out = self.avgpool(outcga)
        out = out.view(out.size(0), -1)
        out = self.fc2(out)
        out = self.relu(out)
        out = self.fc(out)
        return out,outspa,outcga,afspa,afcga

# 处理变长序列的LSTM模型
class SeqClassifierVarLen(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        self.hidden_size2 =  hidden_size*2
        super(SeqClassifierVarLen, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True, bidirectional=True, dropout=0.5, num_layers=2)
        self.fc = nn.Linear(hidden_size*2, self.hidden_size2)
        self.covn1d = nn.Conv1d(input_size, self.hidden_size2, kernel_size=3, padding=1)
        self.fc2 = nn.Linear(self.hidden_size2, num_classes)
        self.dropout = nn.Dropout(0.5)
        self.relu = nn.ReLU()
        

    def forward(self, x, lengths):
        # x: (batch_size, seq_len, input_size)
        packed_input = nn.utils.rnn.pack_padded_sequence(x, lengths, batch_first=True, enforce_sorted=False)
        packed_output, _ = self.lstm(packed_input)  # lstm_out: (batch_size, seq_len, hidden_size)
        lstm_out, _ = nn.utils.rnn.pad_packed_sequence(packed_output, batch_first=True)
        out = self.fc(lstm_out[:, -1, :])  # 取最后一个时间步的输出

        out = self.relu(out)
        out = self.dropout(out)


        out = self.fc2(out)
        out = self.relu(out)
        

        out = F.log_softmax(out, dim=1)
        return out