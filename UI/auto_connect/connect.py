from auto_connect.Conn import *

def connect():
    csi_connect = Conn_Csi(config.csi_raspberry_pi_ip, config.username, config.raspberry_pi_password, config.local_path, config.csi_pi_pcap_path)
    pkt_connect = Conn_Pkt(config.pkt_raspberry_pi_ip, config.username, config.raspberry_pi_password, config.local_path, config.pkt_pi_pcap_path)
    return csi_connect, pkt_connect

def prepare_environment(csi_connect, pkt_connect):
    csi_connect.connect()
    csi_connect.Enter_the_work_dir()
    csi_connect.find_channel()
    csi_connect.setup()
    csi_connect.open_new_dir('new_dataset')
    
    pkt_connect.connect()
    # pkt_connect.prepare_environment()
    pkt_connect.set_monitor_mode(config.wifi_channel)
    return csi_connect, pkt_connect
