import os


def swap_files(file1, file2):
    """
    交换两个文件的名字
    """

    os.rename(file1, file1 + '.bak')
    os.rename(file2, file1)
    os.rename(file1 + '.bak', file2)


if __name__ == '__main__':
    swap_files('output.pcap', 'test.pcap')