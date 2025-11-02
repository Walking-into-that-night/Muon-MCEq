import netCDF4 as nc
import numpy as np


dataset = nc.Dataset(r'atmos\ERA5\data\raw_data.nc')


time_var = dataset.variables['valid_time']
pressure_var = dataset.variables['pressure_level']
lat_var = dataset.variables['latitude']
lon_var = dataset.variables['longitude']
print(pressure_var[:])
print(lat_var[:])
print(lon_var[:])

time_units = time_var.units
time_baseline = nc.num2date(time_var[:], time_units)

temperature_var = dataset.variables['t']
geo_var = dataset.variables['z']
temperature_array = []
geo_array = []
for t in range(len(time_var)):
    current_hour = time_baseline[t].hour
    if current_hour == 6:
        temp_data = temperature_var[t, :, :, :]
        geo_data = geo_var[t, :, :, :]
        temperature_array.append(temp_data)
        geo_array.append(geo_data)

T = np.array(temperature_array)
G = np.array(geo_array)
print(T.shape) # (24,37,361,361) (day, pressure_level ,lat, lon)
print(G.shape)
#np.save('T_2015.npy', T)
#np.save('G_2015.npy', G)
dataset.close()


'''
pressure_var[:]
[1000.  975.  950.  925.  900.  875.  850.  825.  800.  775.  750.  700.
  650.  600.  550.  500.  450.  400.  350.  300.  250.  225.  200.  175.
  150.  125.  100.   70.   50.   30.   20.   10.    7.    5.    3.    2.
    1.]
lat_var[:]
[ 90-0 ]
lon_var[:]
[ 90-180 ]
'''