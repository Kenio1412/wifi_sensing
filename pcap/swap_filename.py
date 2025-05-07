import os


def swap_files(file1, file2):
    """
    交换两个文件的名字
    """

    os.rename(file1, file1 + '.bak')
    os.rename(file2, file1)
    os.rename(file1 + '.bak', file2)


if __name__ == '__main__':
    for file in os.listdir('.'):
        if file.endswith('.pcap'):
            filename = file.split('.pcap')[0]
            lable1 , lable2 = filename.split('_')
            lable2 = int(lable2)
            if lable1 == '2' and  lable2 > 45:
                file1 = filename + '.pcap'
                file2 = '5_' + str(lable2) + '.pcap'
                if os.path.exists(file2):
                    swap_files(file1, file2)
                    print(f"Swapped {file1} with {file2}")
                else:
                    print(f"{file2} does not exist, skipping swap.")

