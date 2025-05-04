import csitool.csitools as csitools
import numpy as np
from csitool.passband import lowpass
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from csitool.read_pcap import NEXBeamformReader
import os

def remove_data_with_high_variance(data):
    data = np.array(data)
    for i in range(len(data) - 2, -1, -1):
        variance = np.var(data[i:])
        if variance > 2:
            return data[0:i]
            break

def process_pcap(filepath, output_dir):
    my_reader = NEXBeamformReader()
    file_name = os.path.splitext(os.path.basename(filepath))[0]
    # my_reader = NEXBeamformReader()
    csi_data = my_reader.read_file(filepath, scaled=True)
    csi_matrix, no_frames, no_subcarriers = csitools.get_CSI(csi_data)
    csi_matrix_first = csi_matrix[:, :, 0, 0]
    csi_matrix_first[csi_matrix_first == -np.inf] = np.nan
    imp_mean = SimpleImputer(missing_values=np.nan, strategy='mean')
    csi_matrix_first = imp_mean.fit_transform(csi_matrix_first)
    # Then we'll squeeze it to remove the singleton dimensions.
    csi_matrix_squeeze = np.squeeze(csi_matrix_first)
    csi_matrix_squeezed = np.transpose(csi_matrix_squeeze)

    for x in range(no_subcarriers - 1):
        csi_matrix_squeezed[x] = lowpass(csi_matrix_squeezed[x], 3, 50, 5)  #调用低通滤波器
        #csi_matrix_squeezed[x] = hampel(csi_matrix_squeezed[x], 10, 3)
        #csi_matrix_squeezed[x] = running_mean(csi_matrix_squeezed[x], 10)

    csi_matrix_squeezed = np.transpose(csi_matrix_squeezed)
    pca = PCA(n_components=3)  #调用主成分分析
    csipca = pca.fit_transform(csi_matrix_squeezed)
    csipca = np.transpose(csipca)
    csipca0 = remove_data_with_high_variance(csipca[0])
    x = csi_data.timestamps  #获取时间戳
    x = csi_data.timestamps - csi_data.timestamps[0]
    x = x[:len(csipca0)]  # 同步裁剪
    # print(x)

    plt.figure(figsize=(10, 6))
    plt.plot(x, csipca0, label='Subcarrier 0')
    # plt.plot(x, csi_matrix_squeezed[:, 0], label='Subcarrier 2')

    plt.title("CSI Waveform for Subcarrier 0", fontsize=14)
    plt.xlabel("Frame Index (Time)", fontsize=12)
    plt.ylabel("Amplitude", fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True)
    output_path = os.path.join(output_dir, f"{file_name}.jpg")
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")


def batch_process_pcap_files(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for file in os.listdir(input_dir):
        if file.endswith(".pcap"):
            full_path = os.path.join(input_dir, file)
            try:
                process_pcap(full_path, output_dir)
            except Exception as e:
                print(f"[ERROR] Failed to process {file}: {e}")


def main(datapath, out_path):
    batch_process_pcap_files(datapath, out_path)
    

if __name__ == "__main__":
    datapath = r'F:\Coding\wifi_sensing\data_set'
    out_path = os.path.join(os.path.dirname(__file__), "output")
    main(datapath, out_path)

# 如果需要绘制多个子载波：
# plt.figure(figsize=(12, 8))
#
# # 假设只绘制前 3 个子载波
# for i in range(3):
#     plt.plot(csi_matrix_squeezed[:, i], label=f'Subcarrier {i+1}')  # 子载波 i 的波形
#
# # 添加图形信息
# plt.title("CSI Waveforms for Multiple Subcarriers", fontsize=14)
# plt.xlabel("Frame Index (Time)", fontsize=12)
# plt.ylabel("Amplitude", fontsize=12)
# plt.legend(fontsize=10)
# plt.grid(True)
#
# # 显示图形
# plt.show()
