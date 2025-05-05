import csitool.csitools as csitools
import numpy as np
from csitool.passband import lowpass
import matplotlib.pyplot as plt
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
    return data

def process_pcap(filepath, output_dir):
    my_reader = NEXBeamformReader()
    file_name = os.path.splitext(os.path.basename(filepath))[0]
    csi_data = my_reader.read_file(filepath, scaled=True)
    csi_matrix, no_frames, no_subcarriers = csitools.get_CSI(csi_data)
    csi_matrix_first = csi_matrix[:, :, 0, 0]
    csi_matrix_first[csi_matrix_first == -np.inf] = np.nan
    imp_mean = SimpleImputer(missing_values=np.nan, strategy='mean')
    csi_matrix_first = imp_mean.fit_transform(csi_matrix_first)
    csi_matrix_squeeze = np.squeeze(csi_matrix_first)
    csi_matrix_squeezed = np.transpose(csi_matrix_squeeze)
    for i in range(20):
        filtered = lowpass(csi_matrix_squeezed[i], 3, 50, 5)
        sub_output_dir = os.path.join(output_dir, f"subcarrier_{i}")
        os.makedirs(sub_output_dir, exist_ok=True)
        x = csi_data.timestamps - csi_data.timestamps[0]
        x = x[:len(filtered)]
        plt.figure(figsize=(10, 4))
        plt.plot(x, filtered, label='')
        plt.title("", fontsize=12)
        plt.xlabel("")
        plt.ylabel("")
        # plt.grid(False)
        plt.tight_layout()
        output_path = os.path.join(sub_output_dir, f"{file_name}_sub_{i}.jpg")
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
    out_path = os.path.join(os.path.dirname(__file__), "jpg_output")
    main(datapath, out_path)