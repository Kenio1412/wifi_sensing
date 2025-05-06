## -csitool

一些处理含`CSI`的`pcap`包的代码

## -process_csi.py

将`pcap`包中的子载波绘制成jpg图和csv数据。

这里可以绘制所有子载波的图，具体只需要修改`csopca[i]`即可，代码里处理的是`csopca[0]`

绘制PCA主成分分析后的CSI数据，并且绘制前20个子载波的jpg图像

## -pcap_to_jpg.py

直接对`pcap`包中的CSI数据进行处理，不进行主成分分析，并且绘制前20个子载波的jpg图像

## netual_model

存放训练CSI对应波形图的训练模型

