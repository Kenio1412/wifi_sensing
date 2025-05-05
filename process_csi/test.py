import csitool.csitools as csitools
import numpy as np
from csitool.passband import lowpass
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from csitool.read_pcap import NEXBeamformReader
import os
import pandas as pd

def remove_data_with_high_variance(data):
    data = np.array(data)
    for i in range(len(data) - 2, -1, -1):
        variance = np.var(data[i:])
        if variance > 2:
            return data[0:i]
            break
    return data

file_path = f"F:\\Coding\\wifi_sensing\\data_set\\1-5.pcap"
my_reader = NEXBeamformReader()
file_name = os.path.splitext(os.path.basename(file_path))[0]
# my_reader = NEXBeamformReader()
csi_data = my_reader.read_file(file_path, scaled=True)
csi_matrix, no_frames, no_subcarriers = csitools.get_CSI(csi_data)
csi_matrix_first = csi_matrix[:, :, 0, 0]
csi_matrix_first[csi_matrix_first == -np.inf] = np.nan
imp_mean = SimpleImputer(missing_values=np.nan, strategy='mean')
csi_matrix_first = imp_mean.fit_transform(csi_matrix_first)
# Then we'll squeeze it to remove the singleton dimensions.
csi_matrix_squeeze = np.squeeze(csi_matrix_first)
csi_matrix_squeezed = np.transpose(csi_matrix_squeeze)
# 调用主成分分析
for x in range(no_subcarriers - 1):
    csi_matrix_squeezed[x] = lowpass(csi_matrix_squeezed[x], 3, 50, 5)

csi_matrix_squeezed = np.transpose(csi_matrix_squeezed)
pca = PCA(n_components=20)
csipca = pca.fit_transform(csi_matrix_squeezed)
# print(csipca.shape)
csipca = np.transpose(csipca)
# print(csipca[2])
output_dir = r'F:\Coding\wifi_sensing\test_output'
for i in range(10):
    x = csi_data.timestamps - csi_data.timestamps[0]
    csipca0 = remove_data_with_high_variance(csipca[i])
    sub_output_dir = os.path.join(output_dir, f"subcarrier_{i}")
    os.makedirs(sub_output_dir, exist_ok=True)
    x = x[:len(csipca0)]
    plt.figure(figsize=(10, 6))
    plt.plot(x, csipca0, label='')

    plt.title("", fontsize=14)
    plt.xlabel("", fontsize=12)
    plt.ylabel("", fontsize=12)
    plt.legend(fontsize=12)
    # plt.grid(True)
    output_path = os.path.join(sub_output_dir, f"{file_name}_sub_{i}.jpg")
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")
