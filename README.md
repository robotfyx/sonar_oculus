# sonar_oculus

用于使用ROS完成oculus_sonar M1200d的图像接收与转化处理，其中绝大部分代码来自[][GitHub - ENSTABretagneRobotics/oculus_ros: ROS1 node for the Blueprint Oculus front scan sonar.](https://github.com/ENSTABretagneRobotics/oculus_ros)，在其基础上作了增添与修改。

---

## 安装步骤

1.首先安装[oculus_driver](https://github.com/ENSTABretagneRobotics/oculus_driver)，它的用处是在没有网络连接的情况下也可以使用oculus_sonar。按照链接中的readme安装即可。

2.下载功能包oculus_ros，在工作空间中catkin_make，需要注意的是原代码中有个错误，直接catkin_make会报如下错误：

![](https://cdn.nlark.com/yuque/0/2023/png/2556769/1694955285204-ab878893-b75e-4c50-b4aa-f38a63f1de7a.png)

按照提示找到conversions.h文件，将155与182行的data_size改为ping_data_size，再重新catkin_make便可以成功了。

![](https://cdn.nlark.com/yuque/0/2023/png/2556769/1694955453723-0ddce1ac-63dc-4614-9a1d-65a5a2e6b160.png?x-oss-process=image%2Fresize%2Cw_737%2Climit_0)

---

## 使用说明

可以通过`rosrun oculus_sonar oculus_sonar_node`启动节点来接收声呐图像（可以从rviz中选择消息进行图像查看），同时通过`rosrun rqt_reconfigure rqt_reconfigure`调出参数调整的gui界面进行手动调整，观察参数效果。

oculus_sonar_node启动的是声呐，发布的是原始的二维数组，通过`rosrun oculus_sonar oculus_viewer.py`可以启动/oculus_viewer节点，该节点订阅/oculus_sonar/ping与/oculus_sonar/ping_image话题的消息，即接收相关参数与原始二维图像，通过之前实现的处理方法转为扇形图，并将该扇形图发布出去。

运行sonar_oculus_ros.launch文件，可以同时启动/oculus_sonar_node、/oculus_viewer节点，rqt_reconfigure参数调整面板与rviz图像显示。