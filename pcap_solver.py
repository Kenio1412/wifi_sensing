import pyshark
import os
import tqdm
import pandas as pd
import scapy.all as wrpcap
import asyncio
from concurrent.futures import ThreadPoolExecutor
import contextvars

class PcapSolver:
    def __init__(self, filePath,filter=None):
        self.filePath = filePath
        self.cap = None
        self.current_loop = contextvars.ContextVar("current_loop")
        if filter:
            self.filter = filter
            self.cap = pyshark.FileCapture(filePath,display_filter=filter)
        else:
            self.cap = pyshark.FileCapture(filePath)

    def info_detailed(self):    
        cap = self.cap
        for packet in tqdm.tqdm(self.cap):
            print("Packet Attributes:")
            print(f"Sniff Time: {packet.sniff_time}")
            print(f"Timestamp: {packet.sniff_timestamp}")
            print(f"Length: {packet.length}")
            print(f"Highest Layer: {packet.highest_layer}")
            print(f"Transport Layer: {packet.transport_layer}")
            print(f"captured_length: {packet.captured_length}")
            print(f"frame_info: {packet.frame_info}")
            print(f"wlan: {packet.wlan}")
            print(f"wlan: {packet.wlan}")
            # print(f"wlan.mgt: {packet.wlan.mgt}")
            print(f"wlan_radio: {packet.wlan_radio}")
            print("Layers:")
            for layer in packet.layers:
                print(f" - {layer.layer_name}")
            break  # 仅查看第一个数据包

    def info_mac(self):
        """
        提取MAC地址信息,并统计各个地址的数量
        """
        cap = self.cap
        # TA = set()
        RA = set()
        # SA = set()
        # DA = set()
        n = 0
        bad = 0
        bob_num = 0
        for  packet in tqdm.tqdm(cap, desc="Processing", unit="items"):
            n += 1
            try:
                # print("WLAN Layer Attributes:")
                # print(f"Transmitter Address (TA): {packet.wlan.ta}")
                # print(f"Receiver Address (RA): {packet.wlan.ra}")
                # print(f"Source Address (SA): {packet.wlan.sa}")
                # print(f"Destination Address (DA): {packet.wlan.da}")
                # ta = packet.wlan.ta
                ra = packet.wlan.ra
                if ra != bob_mac:
                    continue
                bob_num += 1
                # sa = packet.wlan.sa
                # da = packet.wlan.da

                
            except AttributeError:
                # print("No WLAN layer found in this packet.")
                bad += 1
                continue
            else:
                # print(f"Transmitter Address (TA): {ta}")
                # print(f"Receiver Address (RA): {ra}")
                # print(f"Source Address (SA): {sa}")
                # print(f"Destination Address (DA): {da}")
                # TA.add(ta)
                RA.add(ra)
                # SA.add(sa)
                # DA.add(da)
        print(f"Total packets: {n}")
        print(f"Bad packets: {bad}")
        print(f"you have {n-bad} packets with WLAN layer.")
        print(f"Bob's packets: {bob_num}")
        # print("Unique Transmitter Addresses (TA):", len(TA) )
        print("Unique Receiver Addresses (RA):", len(RA))
        # print("Unique Source Addresses (SA):", len(SA))
        # print("Unique Destination Addresses (DA):", len(DA))
        # 将结果写入文件
        with open('1_1_mac.txt', 'w') as f:
            f.write(f"Total packets: {n}\n")
            f.write(f"Bad packets: {bad}\n")
            f.write(f"you have {n-bad} packets with WLAN layer.\n")
            f.write(f"Bob's packets: {bob_num}\n")
            # f.write("Unique Transmitter Addresses (TA):\n")
            # for ta in TA:
            #     f.write(f"{ta}\n")
            f.write("Unique Receiver Addresses (RA):\n")
            for ra in RA:
                f.write(f"{ra}\n")
            # f.write("Unique Source Addresses (SA):\n")
            # for sa in SA:
            #     f.write(f"{sa}\n")
            # f.write("Unique Destination Addresses (DA):\n")
            # for da in DA:
            #     f.write(f"{da}\n")

    def save_pcap(self):
        cap = self.cap
        n = 0
        bad = 0
        good = 0
        packet_to_save = []
        for packet in tqdm.tqdm(cap, desc="Processing", unit="items"):
            n += 1
            try:
                # print("WLAN Layer Attributes:")
                # print(f"Transmitter Address (TA): {packet.wlan.ta}")
                # print(f"Receiver Address (RA): {packet.wlan.ra}")
                # print(f"Source Address (SA): {packet.wlan.sa}")
                # print(f"Destination Address (DA): {packet.wlan.da}")
                # ta = packet.wlan.ta
                ra = packet.wlan.ra
                if ra != bob_mac:
                    continue
                raw_packet = packet.get_raw_packet()
                packet_to_save.append(raw_packet)
                good += 1


            except AttributeError:
                bad += 1
                # print("No WLAN layer found in this packet.")
                continue
            else:
                pass
        with open('1_1_bob.pcap', 'wb') as f:
            wrpcap.wrpcap(f, packet_to_save)
        print("Bob's packets saved to 1_1_bob.pcap")
        print(f"Total packets: {n}")
        print(f"Bad packets: {bad}")
        print(f"you have {good} packets with WLAN layer.")
        print(f"Bob's packets: {len(packet_to_save)}")

    def extract(self,source = None, path=None):
        """
        @brief: 提取数据包中的信息
        @param source: pcap文件路径，默认为None，表示使用初始化时指定的文件路径
        @param path: 保存提取结果的csv文件路径，默认为'csv/1_1_packets.csv'
        每个数据包的时间戳、长度、协议类型、源地址、目的地址等信息
        @return: None
        """
        if not source:
            cap = self.cap
        else:
            cap = pyshark.FileCapture(source,display_filter=self.filter)
        if not path:
            path = 'csv/1_1_packets.csv'
        n = 0
        good = 0
        packet_list = []
        for packet in tqdm.tqdm(cap, desc="Processing", unit="items"):
            n += 1
            try:
                ra = packet.wlan.ra
                if ra != bob_mac: # 只处理Bob接收的包
                    continue
                timestamp = packet.sniff_time
                length = packet.length
                good += 1
                
            except AttributeError:
                # print("No WLAN layer found in this packet.")
                
                continue
            else:
                packet_list.append({'timestamp': timestamp,'length' : length, 'ra' : ra})
        df = pd.DataFrame(packet_list)
        df.to_csv(path)
        print(f"Total packets: {n}")
        print(f"you have {good} packets with WLAN layer.")
        print(f"Bob's packets: {len(packet_list)}")
        print("Bob's packets saved to {path}")

    # async def batch_extract(self,source_dir = None, output_dir=None, max_workers=4):
    #     if not source_dir:
    #         source_dir = 'pcap'
    #     if not output_dir:
    #         output_dir = 'csv'
    #     if not os.path.exists(output_dir):
    #         raise FileNotFoundError(f"Output directory {output_dir} does not exist.")
    #     if not os.path.exists(source_dir):
    #         raise FileNotFoundError(f"Source directory {source_dir} does not exist.")
        
    #     semaphore = asyncio.Semaphore(max_workers)
    #     loop = asyncio.get_event_loop()
    #     self.current_loop.set(loop)
    #     executor = ThreadPoolExecutor()

    #     async def process_file(file):
    #         async with semaphore:
    #             file_path = os.path.join(source_dir, file)
    #             output_path = os.path.join(output_dir, file.replace('.pcap', '.csv'))
    #             print(f"Processing {file_path}")
    #             await self.current_loop.get().run_in_executor(executor,self.extract,file_path,output_path)

    #     tasks = [
    #         process_file(file)
    #         for file in os.listdir(source_dir)
    #         if file.endswith('.pcap')
    #     ]

    #     await asyncio.gather(*tasks)
    #     print('All files processed.')

    def batch_extract(self,source_dir = None, output_dir=None, max_workers=4):
        if not source_dir:
            source_dir = 'pcap'
        if not output_dir:
            output_dir = 'csv'
        if not os.path.exists(output_dir):
            raise FileNotFoundError(f"Output directory {output_dir} does not exist.")
        if not os.path.exists(source_dir):
            raise FileNotFoundError(f"Source directory {source_dir} does not exist.")
        
        for file in tqdm.tqdm(os.listdir(source_dir), desc="Processing", unit="items"):
            if file.endswith('.pcap'):
                file_path = os.path.join(source_dir, file)
                output_path = os.path.join(output_dir, file.replace('.pcap', '.csv'))
                print(f"Processing {file_path}")
                self.extract(file_path,output_path)
                print(f"Bob's packets saved to {output_path}")
        
        
        
if __name__ == "__main__":
    filePath = 'pcap/1_1.pcap'
    bob_mac = 'f0:57:a6:a6:b6:b6'
    filter = 'wlan.addr == f0:57:a6:a6:b6:b6'

    if(os.path.exists(filePath)):
        print(f"File {filePath} does exist.")
    else:
        print(f"{filePath} does not exist!")


    solver = PcapSolver(filePath,filter)
    solver.batch_extract(source_dir='pcap', output_dir='csv')
    # asyncio.run(solver.batch_extract(source_dir='pcap', output_dir='csv'))
    # solver.info_detailed()
    # solver.info_mac()