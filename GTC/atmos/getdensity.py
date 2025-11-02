import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

RE = 6371e3
T = np.load('T_2015.npy')
G = np.load('G_2015.npy')
# shape of T and G is (24,37,161,201) (day, pressure_level ,lat, lon)
# T in K, G (gravitational potential energy for unit mass) in J/kg
# lat and lon range from S0-N40,E90-E140
LON_MIN, LON_MAX = 113.9, 114.1
LAT_MIN, LAT_MAX = 0, 22

pressure_levels = [1000. ,975., 950., 925. , 900. , 875. , 850. , 825. , 800.,  775. , 750. , 700.,
  650. , 600.,  550. , 500. , 450. , 400.,  350. , 300. , 250. , 225. , 200. , 175. ,
  150.,  125. , 100. ,  70. ,  50.  , 30. ,  20. ,  10.  ,  7.  ,  5. ,   3.  ,  2. ,
    1.]

def TP2rou(T, P): # T in K, P in hPa, rou in g/cm^3
    return 0.0003488*(P/T)

def G2H(_G): # G in J/kg, H in m
    return _G/9.80665

Rou = np.zeros_like(T)
for idx, P in enumerate(pressure_levels):
    Rou[:, idx, :, :] = TP2rou(T[:, idx, :, :], P)
Height = G2H(G)

# p in hPa, X in g/cm^2
def p2X(p): 
    return 10*p/9.788

# Xv ,X in same unit
def Xv2X(Xv,T,theta): 
    return Xv/(np.cos(theta)+0.003*np.sqrt(T)*np.power(np.sin(theta),30))

# change lon,lat to index of T and G
# lon,lat in degree, return index of row, col
def lon_lat2index(lon, lat):  
    assert LON_MIN <= lon <= LON_MAX and LAT_MIN <= lat <= LAT_MAX, 'lon,lat out of range'
    return ( (int)(((LAT_MAX-lat)*(T.shape[2]-1))//(LAT_MAX-LAT_MIN)) , (int)(((lon-LON_MIN)*(T.shape[3]-1))//(LON_MAX-LON_MIN)) )


# from (lon0, lat0, last_press_level) climb to (lon, lat) with angle theta, phi
# return oblique distance (in meters), lon, lat
def obliqueClimb(day,lon0, lat0, last_press_level, cumulative_l,theta, phi, max_steps=1000, dt_init=100, err=1):
    assert 0 <= last_press_level < T.shape[1] and 0 <= theta <= 90 and 0 <= phi <= 360

    def delta_lon_per_m(_lat):
        return 1 / (RE * np.cos(np.radians(_lat)) * np.pi / 180)
    delta_lat_per_m = 1 / (RE * np.pi / 180)
    
    theta = np.radians(theta)
    phi = np.radians(phi)
    east = np.sin(theta) * np.sin(phi)
    south = np.sin(theta) * np.cos(phi)

    t = 0
    dt = dt_init
    loop = 0
    row0, col0 = lon_lat2index(lon0, lat0)
    z0 = Height[day, last_press_level, row0, col0]

    lon = lon0
    lat = lat0

    while 1:
        loop += 1
        if loop > max_steps:
            break

        lat = lat0 - t * south * delta_lat_per_m
        lon = lon0 + t * east * delta_lon_per_m(lat)
        z = z0 + t * (np.cos(theta) + (cumulative_l/RE)*np.sin(theta)*np.sin(theta))

        row, col = lon_lat2index(lon, lat)
        if row < 0 or row >= T.shape[2] or col < 0 or col >= T.shape[3]:
            break
        
        next_z = Height[day, last_press_level+1, row, col]
        if next_z > z:
            t += dt
        else:
            if (z-next_z) < err:
                return (t,lon,lat)
            else:
                t -= dt
                dt /= 2
    return (-1,lon,lat)


def get_density_gen(day,lat0,lon0,theta,phi):
    delta_X_list = []
    rou_list = []
    rou_list.append(Rou[day,0,lon_lat2index(lon0,lat0)[0],lon_lat2index(lon0,lat0)[1]])
    cumulativeL = 0
    cur_press_level = 0
    cur_lat = lat0
    cur_lon = lon0

    while cur_press_level < T.shape[1]-1:
        t,lon,lat = obliqueClimb(day,cur_lon,cur_lat,cur_press_level,cumulativeL,theta,phi)
        if t == -1:
            pass
        else:
            last_row, last_col = lon_lat2index(cur_lon, cur_lat)

            cur_press_level += 1
            cur_lat = lat
            cur_lon = lon
            cumulativeL += t

            cur_row, cur_col = lon_lat2index(cur_lon, cur_lat)
            Xv = p2X(pressure_levels[cur_press_level-1])-p2X(pressure_levels[cur_press_level])
            cur_T = (T[day,cur_press_level,cur_row,cur_col] +
                     T[day,cur_press_level-1,last_row,last_col])/2
            delta_X_list.append(Xv2X(Xv,cur_T,np.radians(theta)))
            rou_list.append(Rou[day,cur_press_level,cur_row,cur_col])

    finalT = T[day,T.shape[1]-1,lon_lat2index(cur_lon, cur_lat)[0],lon_lat2index(cur_lon, cur_lat)[1]] 
    delta_X_list.append(Xv2X(Xv,finalT,np.radians(theta)))

    return delta_X_list, rou_list


def listRerank(delta_X_list, rou_list):
    rou_list.append(0)
    rou_list.reverse()

    X_list = [0]
    delta_X_list.reverse()
    delta_X_list = np.cumsum(delta_X_list)
    X_list.extend(delta_X_list)
    
    return X_list, rou_list

def get_density_f(day,lat0,lon0,theta,phi):
    delta_X_list, rou_list = get_density_gen(day,lat0,lon0,theta,phi)
    X_list, rou_list = listRerank(delta_X_list, rou_list)
    f = interp1d(X_list, rou_list, kind='linear')
    return f,X_list[-1]


# Example usage:
get_density,Xmax = get_density_f(0,22,114,45,0)
Xs = np.linspace(0,Xmax,50)
Ys = get_density(Xs)
plt.plot(Xs,Ys)
plt.xlabel('X (g/cm^2)')
plt.ylabel('Density (g/cm^3)')
plt.title('Density vs. X for lat=22, lon=114, theta=45, phi=0, 20150101-6:00')

plt.show()
