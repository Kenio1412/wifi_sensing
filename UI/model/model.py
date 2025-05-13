import torch
import torch.nn.functional as F
import torch.nn as nn
import torchvision.models as models
import torch.optim as optim
import torchvision.transforms as transforms
from tensorboardX import SummaryWriter
from da_att import SpatialGate, ChannelGate


class DACN(nn.Module):
    def __init__(self, num_classes=10):
        super(DACN, self).__init__()
        self.spa = SpatialGate()
        self.cga = ChannelGate(512)

        resnet = models.resnet18(weights='DEFAULT')
        self.features = nn.Sequential(*list(resnet.children())[:-2])  
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc2 = nn.Linear(512, 512)
        self.fc = nn.Linear(512, num_classes)
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