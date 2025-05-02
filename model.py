import torch
import torch.nn as nn
import torch.nn.functional as F


# 处理变长序列的LSTM模型
class SeqClassifierVarLen(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        self.hidden_size2 =  hidden_size*2
        super(SeqClassifierVarLen, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, self.hidden_size2)
        self.covn1d = nn.Conv1d(self.hidden_size2, self.hidden_size2, kernel_size=3, padding=1)
        self.fc2 = nn.Linear(self.hidden_size2, num_classes)
        self.dropout = nn.Dropout(0.5)
        

    def forward(self, x, lengths):
        # x: (batch_size, seq_len, input_size)
        packed_input = nn.utils.rnn.pack_padded_sequence(x, lengths, batch_first=True, enforce_sorted=False)
        packed_output, _ = self.lstm(packed_input)  # lstm_out: (batch_size, seq_len, hidden_size)
        lstm_out, _ = nn.utils.rnn.pad_packed_sequence(packed_output, batch_first=True)
        out = self.fc(lstm_out[:, -1, :])  # 取最后一个时间步的输出
        out = self.dropout(out)

        out = self.fc2(out)
        out = F.log_softmax(out, dim=1)
        return out