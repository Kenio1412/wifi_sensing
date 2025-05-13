import paramiko
import time
import os
# from eval import eval
import config as config

class Conn_Csi:
    def __init__(self, raspberry_pi_ip, username, raspberry_pi_password, local_path, pcap_path):
        """
        @brief: 初始化连接类
        @param raspberry_pi_ip: 树莓派IP地址
        @param username: 树莓派用户名
        @param raspberry_pi_password: 树莓派密码
        @param local_path: 本地保存路径
        @param pcap_path: 树莓派抓包文件路径
        @return: None
        """
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sftp = None
        self.channel = None
        self.raspberry_pi_ip = raspberry_pi_ip
        self.username = username
        self.password = raspberry_pi_password
        self.local_path = config.csi_pi_pcap_path
        self.wifichannel = config.wifi_channel
    
    def connect(self):
        """
        @brief: 连接树莓派
        @return: None
        """
        try:
            self.ssh.connect(self.raspberry_pi_ip, username=self.username, password=self.password)
            print("Connected to Raspberry Pi")
        except paramiko.SSHException as e:
            print(f"Failed to connect to Raspberry Pi: {e}")
            exit(1)
        self.sftp = self.ssh.open_sftp()
        self.channel = self.ssh.invoke_shell()
        output = self.channel.recv(1024).decode()
        self.channel.send("sudo su\n")
        

    def disconnect(self):
        """
        @brief: 断开连接
        @return: None
        """
        if self.sftp:
            self.sftp.close()
        if self.channel:
            self.channel.close()
        if self.ssh:
            self.ssh.close()
        print("Connection closed")

    def Enter_the_work_dir(self):
        """
        @brief: 进入指定目录
        @return: None
        """
        self.channel.send(f"cd /home/pi/CSI_Collection\n")
        # exit(1)
        time.sleep(2)  # 等待一段时间以确保网卡进入监听模式
        print("Have entered the work directory")

    def find_channel(self):
        """
        @brief: 查找信道
        @return: None
        """
        self.wifichannel = 11

    def setup(self):
        """
        @brief: 运行脚本
        @sudo bash setup.sh --laptop-ip None --raspberry-ip None --mac-adr F0:57:A6:A6:B6:B6 --channel 6 --bandwidth 20 --core 1 --spatial-stream 1 
        @return: None
        """
        cmd = "sudo bash setup.sh --laptop-ip None --raspberry-ip None --mac-adr "
        cmd += config.Mac
        cmd += " --channel "
        cmd += str(self.wifichannel)
        if  0 < int(self.wifichannel) < 14:
            cmd += " --bandwidth 20 --core 1 --spatial-stream 1"
        else:
            cmd += " --bandwidth 40 --core 1 --spatial-stream 1"
        self.channel.send(cmd + "\n")
        time.sleep(2)  
        output = self.channel.recv(1024).decode()
        print("[*]输出结果：", output)
    
    def pwd(self):
        """
        @brief: 获取当前目录
        @return: None
        """
        self.channel.send("pwd\n")
        time.sleep(2)
        output = self.channel.recv(1024).decode()
        lines = output.strip().splitlines()
        path = lines[-1] if lines else ""
        return path
    
    def open_new_dir(self, dir_name):
        """
        @brief: 创建新目录并且进入
        @param dir_name: 新目录名称
        @return: None
        """  
        self.channel.send(f"ls | grep {dir_name}\n")
        
        output = self.channel.recv(1024)
        if output.decode().strip() == "":
            print(f"[*]目录不存在，创建新目录：{dir_name}")
            self.channel.send(f"sudo mkdir {dir_name}\n")
            time.sleep(2)
        else:
            print(f"[*]目录已存在：{dir_name}")
        self.channel.send(f"cd {dir_name}\n")
        output = self.channel.recv(1024)
        time.sleep(2)
    
    def start_capture(self, choice, duration=10 ):
        """
        @brief: 开始抓包
        @param choice: 抓包方式，time表示时间，count表示抓取指定数量
        @param duration: 抓包时长
        @return: None
        """    
        full_path = config.csi_pi_pcap_path + "/csi.pcap"
        if choice == "time":
            self.channel.send(f"sudo timeout {duration} tcpdump -i wlan0 dst port 5500 -vv -w {full_path}\n")
            time.sleep(duration + 2)
            print(f"Packet capture started for {duration} seconds and saved to {full_path}")
        else:
            self.channel.send(f"sudo tcpdump -i wlan0 dst port 5500 -vv -w {full_path} -c 1000\n")
            time.sleep(duration + 2)
            print(f"Packet capture started and saved to {full_path}")
    
    def stop_capture(self):
        """
        @brief: 停止抓包
        @return: None
        """
        self.channel.send("sudo killall tcpdump\n")
        time.sleep(2)

    def transfer_file(self, local_path=None):
        """
        @brief: 传输文件到本地
        @return: None
        """
        file_path = config.csi_pi_pcap_path + "/csi.pcap"
        try:
            self.sftp.get(file_path, os.path.join(config.local_path, "csi.pcap"))
            print(f"File {config.csi_pi_pcap_path + '/csi.pcap'} transferred to {os.path.join(config.local_path, "csi.pcap")}")
        except Exception as e:
            print(f"Failed to transfer file: {e}")



class Conn_Pkt:
    def __init__(self, raspberry_pi_ip, username, raspberry_pi_password, local_path, pcap_path = None):
        """
        @brief: 初始化连接类
        @param raspberry_pi_ip: 树莓派IP地址
        @param username: 树莓派用户名
        @param raspberry_pi_password: 树莓派密码
        @param local_path: 本地保存路径
        @param pcap_path: 树莓派抓包文件路径
        @return: None
        """
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sftp = None
        self.channel = None
        self.raspberry_pi_ip = raspberry_pi_ip
        self.username = username
        self.password = raspberry_pi_password
        self.local_path = config.local_path
        self.pcap_path = pcap_path
    
    def connect(self):
        """
        @brief: 连接树莓派
        @return: None
        """
        try:
            self.ssh.connect(self.raspberry_pi_ip, username=self.username, password=self.password)
            print("Connected to Raspberry Pi")
        except paramiko.SSHException as e:
            print(f"Failed to connect to Raspberry Pi: {e}")
            exit(1)
        self.sftp = self.ssh.open_sftp()
        self.channel = self.ssh.invoke_shell()
        self.channel.send("sudo su\n")

    def disconnect(self):
        """
        @brief: 断开连接
        @return: None
        """
        if self.sftp:
            self.sftp.close()
        if self.channel:
            self.channel.close()
        if self.ssh:
            self.ssh.close()
        print("Connection closed")
    
    def prepare_environment(self):
        """
        @brief: 准备环境
        @return: None
        """
        cmd = ""
        cmd += "sudo su"
        cmd += "&& cd /home/pi/nexmon/" 
        cmd += "&& source setup_env.sh"
        cmd += "&& cd patches/bcm43455c0/7_45_206/nexmon/"
        cmd += "&& make install-firmware"
        
        self.channel.send(cmd + "\n")
        time.sleep(25)
        print("Environment prepared successfully.")

    def set_monitor_mode(self, channel):
        """
        @brief: 设置网卡监听模式
        @param channel: 信道
        @return: None
        """
        self.channel.send(f"sudo airmon-ng start wlan1 {channel}\n")
        time.sleep(2) 
        print("Network interface set to monitor mode.")

    def start_capture(self, duration=10):
        """
        @brief: 开始抓包
        @param duration: 抓包时长
        @return: None
        """    
        pcap_path = config.pkt_pi_pcap_path + "/pkt.pcap"
        self.channel.send(f"sudo tcpdump -i wlan1mon -w {pcap_path} -G {duration} -W 1\n")
        time.sleep(duration + 2)  # 等待抓包完成
        print(f"Packet capture started for {duration} seconds and saved to {pcap_path}")
    
    def stop_capture(self):
        """
        @brief: 停止抓包
        @return: None
        """
        self.channel.send("sudo killall tcpdump\n")
        time.sleep(2)

    def transfer_file(self):
        """
        @brief: 传输文件到本地
        @return: None
        """
        try:
            local_path = os.path.join(config.local_path, "pkt.pcap")
            pcap_path = config.pkt_pi_pcap_path + "/pkt.pcap"
            self.sftp.get(pcap_path, local_path)
            print(f"File {pcap_path} transferred to {local_path}")
        except Exception as e:
            print(f"Failed to transfer file: {e}")


    
