import paramiko
import time
import os
from eval import eval
import config



class Conn:
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
        self.local_path = local_path
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

    def set_monitor_mode(self, channel):
        """
        @brief: 设置网卡监听模式
        @param channel: 信道
        @return: None
        """
        cmd = ""
        cmd += "sudo su"
        cmd += "&& cd /home/pi/nexmon/" 
        cmd += "&& source setup_env.sh"
        cmd += "&& cd patches/bcm43455c0/7_45_206/nexmon/"
        cmd += "&& make install-firmware"

        # self.channel.send(cmd + f"sudo airmon-ng start wlan0 {channel}\n")
        # time.sleep(10)  # 等待一段时间以确保命令执行完成
        # print("Firmware installed successfully.")

        self.channel.send(f"sudo airmon-ng start wlan0 {channel}\n")

        # exit(1)
        time.sleep(2)  # 等待一段时间以确保网卡进入监听模式
        print("Network interface set to monitor mode.")
    
    def start_capture(self, duration=10 , pcap_path=None):
        """
        @brief: 开始抓包
        @param duration: 抓包时长
        @return: None
        """
        if pcap_path:
            self.pcap_path = pcap_path
        
        self.channel.send(f"sudo tcpdump -i wlan0mon -w {self.pcap_path} -G {duration} -W 1\n")
        # stdout, stderr = self.channel.recv_exit_status()
        # if stderr:
        #     print(f"Error starting packet capture: {stderr.decode()}")
        #     exit(1)
        #     return
        time.sleep(duration + 2)  # 等待抓包完成
        print(f"Packet capture started for {duration} seconds and saved to {self.pcap_path}")
    
    def stop_capture(self):
        """
        @brief: 停止抓包
        @return: None
        """
        self.channel.send("sudo killall tcpdump\n")
        time.sleep(2)

    def transfer_file(self,local_path=None):
        """
        @brief: 传输文件到本地
        @return: None
        """
        if local_path:
            self.local_path = local_path
        try:
            self.sftp.get(self.pcap_path, self.local_path)
            print(f"File {self.pcap_path} transferred to {self.local_path}")
        except Exception as e:
            print(f"Failed to transfer file: {e}")

    def run(self):
        """
        @brief: 运行连接类
        @return: None
        """
        self.connect()
        self.set_monitor_mode(13)
        self.start_capture(10)
        self.stop_capture()
        self.transfer_file()
        self.disconnect()


if __name__ == "__main__":
    


    
    # 本地路径保存地址
    local_path = config.eval_pcap_path + '/temp.pcap'

    # 检查本地路径是否存在，若存在则删除
    if os.path.exists(local_path):
        os.remove(local_path)
        print("File removed successfully")
    else:
        print("File does not exist")

    # 树莓派抓包文件路径
    pi_pcap_path = config.pi_pcap_path

    raspberry_pi_ip = config.raspberry_pi_ip
    username = config.username
    raspberry_pi_password = config.raspberry_pi_password
    

    conn = Conn(raspberry_pi_ip, username, raspberry_pi_password, local_path, pi_pcap_path)

    if not os.path.exists(local_path):
        print("file not exist")
    

