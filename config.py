import os

rootpath = os.getcwd()
eval_path = os.path.join(rootpath, "eval_data")
eval_pcap_path = os.path.join(eval_path, "pcap")
eval_csv_path = os.path.join(eval_path, "csv")
eval_csv_group_path = os.path.join(eval_path, "csv_group")
eval_csv_img_path = os.path.join(eval_path, "csv_img")

# 目标MAC地址
kenioMac = '3e:d2:e5:91:9f:c3'
# bobMac = 'f0:57:a6:a6:b6:b6'
bobMac = kenioMac

channel = 13  # 树莓派抓包的信道
capture_time = 10  # 抓包时间，单位为秒


raspberry_pi_ip = "raspberrypi.local"  # 替换为树莓派的IP地址
username = "pi"  # 替换为树莓派的用户名
raspberry_pi_password = "raspberry"  # 替换为树莓派的密码

pi_pcap_path = "/home/pi/eval"  # 替换为要传输的文件路径


