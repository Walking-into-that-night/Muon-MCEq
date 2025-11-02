import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.ticker import LogFormatter
import pandas as pd

#           EH1    EH2      EH3
#altitude   3      -42      -32

# z0 in m, theta in degrees, phi in degrees
def calculate_oblique_depth(elevation, src, lon0, lat0, z0, theta, phi, max_steps=100, dt_init=100, err=0.01):
    R = 6371e3
    delta_lon_per_m = 1 / (R * np.cos(np.radians(lat0)) * np.pi / 180)
    delta_lat_per_m = 1 / (R * np.pi / 180)
    
    theta = np.radians(theta)
    phi = np.radians(phi)
    east = np.sin(theta) * np.sin(phi)
    south = np.sin(theta) * np.cos(phi)
    dz = np.cos(theta)
    t = 0
    dt = dt_init
    loop = 0
    while 1:
        loop += 1
        if loop > max_steps:
            return t
        lon = lon0 + t * east * delta_lon_per_m
        lat = lat0 - t * south * delta_lat_per_m
        z = z0 + t * dz

        try:
            row, col = src.index(lon, lat)
            if row < 0 or row >= elevation.shape[0] or col < 0 or col >= elevation.shape[1]:
                break
            real_height = elevation[int(round(row)), int(round(col))]
        except:
            break

        if real_height > z:
            t += dt
        else:
            if (z-real_height)<err:
                return t
            else:
                t -= dt
                dt /= 2
    return np.inf  

def h2eth(h): # eth in GeV, h in m
    return 500*(np.exp(0.00106*h)-1)

with rasterio.open(r'mount\ASTGTMV003_N22E114\ASTGTMV003_N22E114_dem.tif') as src:
    # 读取高程数据到NumPy数组
    elevation = src.read(1)

lon1, lat1 = 114.544, 22.6017
row1, col1 = src.index(lon1, lat1)
lon2, lat2 = 114.55, 22.609
row2, col2 = src.index(lon2, lat2)
lon3, lat3 = 114.54, 22.616
row3, col3 = src.index(lon3, lat3)
if 0:
    print('row1:',row1,'col1:',col1,'elevation1:',elevation[row1,col1])
    print('row2:',row2,'col2:',col2,'elevation2:',elevation[row2,col2])
    print('row3:',row3,'col3:',col3,'elevation3:',elevation[row3,col3])



if 0:
    plt.figure(figsize=(10, 10))  
    plt.imshow(elevation, cmap='terrain', extent=[src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top])  # 使用terrain颜色映射
    plt.scatter(lon1, lat1, c='red', s=3, marker='x')
    plt.scatter(lon2, lat2, c='purple', s=3, marker='x')
    plt.scatter(lon3, lat3, c='white', s=3, marker='x')
    plt.colorbar(label='Elevation') 
    plt.title('Elevation Map')  
    plt.xlabel('Longitude')  
    plt.ylabel('Latitude')  
    plt.show()  

if 1:
    theta_range = np.linspace(0, 90, 90)  # 天顶角0~90度（半径方向）
    phi_range = np.linspace(0, 360, 360)  # 方位角0~360度（极角方向）
    Theta, Phi = np.meshgrid(theta_range, phi_range)

    Z = np.zeros_like(Theta)
    Eth = np.zeros_like(Z)
    for i in range(Theta.shape[0]):
        for j in range(Theta.shape[1]):
            theta_deg = Theta[i,j]
            phi_deg = Phi[i,j]
            # 计算斜深（调用函数）
            Z[i,j] = calculate_oblique_depth(
                elevation, src, lon3, lat3, -32, 
                theta_deg, phi_deg, max_steps=1000, dt_init=100, err=0.01
            )
    Eth = h2eth(Z)
    df = pd.DataFrame(
    Eth, 
    index=phi_range,    # 行索引 = φ值
    columns=theta_range # 列标题 = θ值
    )
    df.to_csv('EH3.csv', index=True, header=True)

    plt.figure(figsize=(10,8))
    ax = plt.subplot(111, projection='polar')
    # 将角度转为弧度
    Phi_rad = np.radians(Phi)
    # 绘制热图（θ为半径，φ为极角，Z为颜色深度）
    c = ax.pcolormesh(Phi_rad, Theta, Eth, cmap='viridis', shading='auto',vmin=0, vmax=1500)
    # 标注极轴
    ax.set_theta_zero_location('S')    # 0度指向南方
    ax.set_theta_direction('counterclockwise')# 顺时针旋转
    ax.set_rlabel_position(90)         # 半径刻度显示位置
    ax.set_title("Eth (θ, φ)", pad=20)
    # 添加颜色条
    plt.colorbar(c, label='Eth (GeV)')
    plt.show()

if 0:
    for i in np.linspace(0,90,10):
        for j in np.linspace(0,360,10):
            depth=calculate_oblique_depth(elevation, src, lon1, lat1, 3, i, j)
            eth=h2eth(depth)
            print('theta:',i,'phi:',j,'depth:',depth,'eth:',eth)