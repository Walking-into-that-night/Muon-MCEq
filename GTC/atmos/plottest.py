import numpy as np
import matplotlib.pyplot as plt


T = np.load('T_2015.npy')
G = np.load('G_2015.npy')
# (24,37,161,921) (day, pressure_level ,lat, lon)
print(T.shape)

day = 0
pressure_levels = [1000. ,975., 950., 925. , 900. , 875. , 850. , 825. , 800.,  775. , 750. , 700.,
  650. , 600.,  550. , 500. , 450. , 400.,  350. , 300. , 250. , 225. , 200. , 175. ,
  150.,  125. , 100. ,  70. ,  50.  , 30. ,  20. ,  10.  ,  7.  ,  5. ,   3.  ,  2. ,
    1.]

# 提取目标压力水平的数据
T_pressure_0 = G[0,5,:,:]/9.80665
latitudes = np.linspace(0, 40, G.shape[2])  # 假设纬度从-90到90
longitudes = np.linspace(100, 130, G.shape[3])  # 假设经度从-180到180
longitudes, latitudes = np.meshgrid(longitudes, latitudes)
# 绘制图像
plt.figure(figsize=(10, 6))
c = plt.pcolormesh(longitudes, latitudes, T_pressure_0, shading='auto')
plt.colorbar(c, label='G')
plt.title('G at Day 0, Pressure Level 1000 hPa')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.show()