import os
import argparse
import gc

import calendar

import cdsapi
import xarray as xr

import numpy as np
import time

class DataSet:
    ''' ERA5 每日后处理数据

    ERA5DataSet类的主要功能是下载数据文件以及管理已下载的文件。
    构造函数接受的参数为年，月，日参数，注意不支持列表输入。读取
    时请务必按日读取。

    Methods:
        __init__(self,*args,**kwargs): 构造函数, 读取文件或者下载文件, 有两种输入, 按照date或者doy
            __init__(self, year, month, day) 接受字典类型或者按照顺序传入值
            __init__(self, year, doy)        接受字典类型或者按照顺序传入值

        __download__(self,type): 内置下载函数

    Attributes:
        setCut (int):          日期分割数, 一个set中涵盖的日期。取4或者8
        year (int):            数据对应的年份
        month(int):            数据对应的月份
        day(int):              数据对应的日期
        dateStr (str)          数据的日期字符串
        daySetNum (int):       多日数据集合的编号
        daySetIndex (int):     单日数据在多日数据集合中的位置
        tempFilePath (str):    温度数据对应的文件绝对路径
        geopFilePath (str):    重力势能数据对应的文件绝对路径
        temperature (xarray):  该日的温度分层分布
        geopotential (xarray): 该日的重力势分层分布
        altitude(xarray):      各气压层的高度分布
        pressure (xarray):     气压层列表
        longtitude (xarray):   经度列表
        latitude (xarray):     维度列表
    '''
    
    def __init__(self, *args,**kwargs):
        ''' ERA5 数据类型构造函数
        构造函数接受的参数为年, 月, 日参数, 或者是某年份的doy,注意不支持列表输入。读取时请务必按日读取。
        '''
        self.setCut = 8

        # 处理输入，将各种类型的输入转换为yymmdd格式
        if ("year" in kwargs.keys()) and ("month" in kwargs.keys()) and ("day" in kwargs.keys()):
            self.year = kwargs['year']
            self.month = kwargs['month']
            self.day = kwargs['day']
        elif len(args) == 3:
            self.year = args[0]
            self.month = args[1]
            self.day = args[2]
        elif ("year" in kwargs.keys()) and ("doy" in kwargs.keys()):
            self.year = kwargs['year']
            doy = kwargs['doy']
            doyList = np.array([(int)(np.sum([calendar.monthrange(self.year,i)[1] for i in range(1,j+1)])) for j in range(13)])
            self.month = np.where(doyList >= doy)[0][0]
            self.day = doy - doyList[self.month-1]
        elif len(args) == 2:
            self.year = args[0]
            doy = args[1]
            doyList = np.array([(int)(np.sum([calendar.monthrange(self.year,i)[1] for i in range(1,j+1)])) for j in range(13)])
            self.month = np.where(doyList >= doy)[0][0]
            self.day = doy - doyList[self.month-1]    
        else:
            raise ValueError("Input must be 'year=,month=,day=' or 'year,month,day' or 'year=,doy=' or 'year,doy'.")

        self.dateStr = f'{self.year}{self.month:02d}{self.day:02d}'

        # 获取当前包路径，找到其中的Data数据库
        projectRootPath = os.getcwd().split('Muon-MCEq/')[0]
        dataRootPath = os.path.join(projectRootPath,'Muon-MCEq/Data/')

        # 按照指定的分割方式生成分割数和分割位置
        self.daySetNum = (self.day-1)//self.setCut
        self.daySetIndex = (self.day-1)%self.setCut

        # 尝试创建新的温度和重力势文件夹
        try: 
            temperaturePath = os.path.join(dataRootPath,"Temperature")
            os.mkdir(temperaturePath)
        except FileExistsError: pass
        try: 
            geopotentialPath = os.path.join(dataRootPath,"Geopotential")
            os.mkdir(geopotentialPath)
        except FileExistsError: pass

        # 尝试创建新的年月日文件夹
        try:
            tempYearPath = os.path.join(temperaturePath,f"{self.year}")
            geopYearPath = os.path.join(geopotentialPath,f"{self.year}")
            os.mkdir(tempYearPath)
            os.mkdir(geopYearPath)
        except FileExistsError: pass
        try:
            tempMonthPath = os.path.join(tempYearPath,str(self.month).zfill(2))
            geopMonthPath = os.path.join(geopYearPath,str(self.month).zfill(2))
            os.mkdir(tempMonthPath)
            os.mkdir(geopMonthPath)
        except FileExistsError: pass
        try:
            tempDayPath = os.path.join(tempMonthPath,f"Set{self.daySetNum}")
            geopDayPath = os.path.join(geopMonthPath,f"Set{self.daySetNum}")
            os.mkdir(tempDayPath)
            os.mkdir(geopDayPath)
        except FileExistsError: pass

        # 得到当前日期的两个文件的绝对路径，已经保证其父目录存在
        self.tempFilePath = os.path.join(tempDayPath,'temperature_0_daily-mean.nc')
        self.geopFilePath = os.path.join(geopDayPath,'geopotential_stream-oper_daily-mean.nc')

        # 尝试打开这个文件夹内的文件，如果找不到就下载
        try:
            tempDataSet = xr.open_dataset(self.tempFilePath,engine='netcdf4')
        except FileNotFoundError:
            self.__download__("temperature")
            tempDataSet = xr.open_dataset(self.tempFilePath,engine='netcdf4')

        try:
            geopDataSet = xr.open_dataset(self.geopFilePath,engine='netcdf4')
        except FileNotFoundError:
            self.__download__("geopotential")
            geopDataSet = xr.open_dataset(self.geopFilePath,engine='netcdf4')

        # 只取当前日期的数据
        self.temperature = tempDataSet.sel(valid_time = self.dateStr)
        self.geopotential = geopDataSet.sel(valid_time = self.dateStr)

        self.temperature = tempDataSet['t'].squeeze()
        self.altitude = geopDataSet['z'].squeeze()/9.8066
        self.pressure = self.temperature['pressure_level'].squeeze()*1e2 # pa
        self.longitude = self.temperature['longitude'].squeeze()
        self.latitude  = self.temperature['latitude'].squeeze()

        R = 8.314 #J/(mol*K)
        M_air = 0.02896 #kg/mol
        self.density = self.pressure * M_air /(R * self.temperature)

        # 然后可以删除内存中的tempDataSet和geopDataSet
        del tempDataSet,geopDataSet
        gc.collect()

    def __download__(self,type):
        ''' ERA5 数据下载函数
        构造函数接受的参数为类型,即geopotential或者temperature
        '''
        print(f'Downloading {self.dateStr} ... \n')
        btime = time.time()

        if type == "geopotential": path = self.geopFilePath
        elif type == "temperature": path = self.tempFilePath
        else: raise TypeError

        daysOfAMonth = calendar.monthrange(self.year,self.month)[1]
        if (self.daySetNum < (daysOfAMonth//self.setCut)):
            daysRange = [f'{d:02d}' for d in np.arange((self.daySetNum*self.setCut+1),(self.daySetNum*self.setCut+self.setCut+1))]
        else:
            daysRange = [f'{d:02d}' for d in np.arange(self.daySetNum*self.setCut+1,daysOfAMonth+1)]

        dataset = "derived-era5-pressure-levels-daily-statistics"
        request = {
            "product_type": "reanalysis",
            "variable": [type],
            "year": f"{self.year}",
            "month": f"{self.month}",
            "day": daysRange,
            "pressure_level": [
                "1", "2", "3",
                "5", "7", "10",
                "20", "30", "50",
                "70", "100", "125",
                "150", "175", "200",
                "225", "250", "300",
                "350", "400", "450",
                "500", "550", "600",
                "650", "700", "750",
                "775", "800", "825",
                "850", "875", "900",
                "925", "950", "975",
                "1000"
            ],
            "daily_statistic": "daily_mean",
            "time_zone": "utc+08:00",
            "frequency": "1_hourly",
            "area": [40, 100, 0, 130]
        }

        client = cdsapi.Client()
        client.retrieve(dataset,request,path)

        etime = time.time()
        print(f'Successfully download {self.dateStr} in {etime-btime:.2f}s \n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ERA5 data downloder')
    parser.add_argument('-y','--year',
                        type=int,
                        required=True,
                        default=2024)
    parser.add_argument('-ds','--doystart',
                        default=1,
                        type=int)
    parser.add_argument('-de','--doyend',
                        default=366,
                        type=int)
    parser.add_argument('-s','--step',
                        default=1,
                        type=int)
    args = parser.parse_args()

    for doy in range(args.doystart,args.doyend,args.step):
        a = DataSet(args.year,doy)
        percentage = (doy - args.doystart + args.step)/(args.doyend - args.doystart) 
        print(f'Finish {percentage:.2%}')