这个文件夹用于储存共有代码，比如有用的函数库
引用这个包内的文件可以用下面的代码：

```
import os
import sys
projectRootPath = os.getcwd().split('Muon-MCEq/')[0]
sys.path.append(os.path.join(projectRootPath,'Muon-MCEq/Public/'))

import ERA5DataSet
```

## ERA5DataSet.py 

这个文件用于下载数据文件，可以作为库单独引用，也可以独自运行。例如：

```
(base) user@user:~$ conda activate MCEq
(MCEq) user@user:~$ python PATH_TO_Public/ERA5DataSet.py -y 2024
```

上面的代码就会下载2024年全年的ERA5数据。已下载的数据不会重复下载。如果要下载指定起始日，停止日以及步长，可以仿照下面的命令：

```
(MCEq) user@user:~$ python PATH_TO_Public/ERA5DataSet.py -y 2024 -ds 100 -de 200 -s 10
```

就可以下载doy100到doy200之间10步长的数据。注意一个数据包包含8天的数据，所以有需要的请自行设置合理的步长。