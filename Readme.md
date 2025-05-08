## -csi_data_set
    存放含CSI的pcap文件，以格式`<label>-<idx>.pcap`存储即可。

## -csi_img
    `csi`对应`pcap`文件处理为`.jpg`图像后存放到该文件夹，格式为`<label>-<idx>`.jpg。
## -pkt_img
    数据包对应`pcap`文件处理为`.jpg`图像后存放到该文件夹，格式为`<label>-<idx>`.jpg。
## -process_csi.py
    处理CSI对应的pcap文件
    --- csitool 存放一些处理pcap获取csi数据的文件
    --- csipcap_to_jpg.py 将csi对应的pcap放入文件夹`csi_data_set`中，

## netual_model

存放训练最终的训练模型
--- csi_loader.py 处理`csi`对应的`jpg`
--- pkt_loader.py 处理数据包对应的`jpg`

--- run_csi.py 训练`CSI`对应图像
--- run_pkt.py 训练数据包图像

--- model.py 用到的模型

--- fusion_loader.py
--- inference_fusion.py 用于测试两个模型“融合”之后的结果
