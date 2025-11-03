import os

import calendar

import cdsapi
import netCDF4 as nc

# 多线程
import threading
from queue import Queue

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

projectRootPath = os.getcwd().split('Muon-MCEq/')[0]
dataRootPath = os.path.join(projectRootPath,'Muon-MCEq/Data/')

def cheakERA5Data(var, year, month, day):
    request = {
            "product_type": "reanalysis",
            "variable": [var],
            "year": f"{year}",
            "month": f"{month:02d}",
            "day": [f'{day:02d}'],
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

    # 定义文件名格式为 年月日.nc，并设置下载路径
    fileName = f"ERA5{str(var).capitalize()}{year}{month:02d}{day:02d}.nc"
    filePath = os.path.join(dataRootPath, fileName)

    print(f"Checking if file {fileName} exists and is complete...")
    # 检查文件是否已存在，且文件完整
    if os.path.exists(filePath):
        try:
            # 尝试打开文件以验证其完整性
            with nc.Dataset(filePath, 'r') as ds:
                print(f"File {fileName} is complete and valid.")
        except OSError as e:
            # 如果文件不完整或损坏，删除并重新下载
            print(f"File {fileName} is corrupted. Redownloading...")
            os.remove(filePath)
            downloadERA5Data(request, filePath)
    else:
        # 如果文件不存在，则直接下载
        print(f"File {fileName} does not exist. Starting download...")
        downloadERA5Data(request, filePath)

def downloadERA5Data(request, filepath):
    dataset = "derived-era5-pressure-levels-daily-statistics"
    print(f"Downloading data to {filepath}...")
    client = cdsapi.Client()
    client.retrieve(dataset, request).download(filepath)
    print(f"Download completed for {filepath}")


queue = Queue()

class DownloadWorker(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            year, month, day = self.queue.get()
            print(f"Worker {threading.current_thread().name} processing download for {year}-{month:02d}-{day:02d}...")
            try:
                cheakERA5Data('geopotential',year, month, day)
                cheakERA5Data('temperature',year, month, day)
            except Exception as e:
                print(f"Error downloading data for {year}-{month:02d}-{day:02d}: {e}")
            finally:
                print(f"Worker {threading.current_thread().name} finished processing download for {year}-{month:02d}-{day:02d}.")
                self.queue.task_done()

# 创建四个工作线程
print("Creating worker threads...")
for x in range(4):
    worker = DownloadWorker(queue)
    worker.daemon = True
    worker.start()
    print(f"Worker thread {worker.name} started.")

# 循环遍历2020到2022年，将任务加入队列
print("Adding download tasks to the queue...")
for year in range(2020, 2022):
    for month in range(1, 13):
        # 获取当前月份的最大天数
        _, max_day = calendar.monthrange(year, month)
        for day in range(1, max_day + 1):
            print(f"Adding task for {year}-{month:02d}-{day:02d} to the queue...")
            queue.put((year, month, day))

# 等待所有任务完成
print("Waiting for all tasks to complete...")
queue.join()
print("All download tasks completed.")