这个文件夹用于储存共有代码，比如有用的函数库
引用这个包内的文件可以用下面的代码：

```
import os
import sys
currentPath = os.getcwd().split('Muon-MCEq/')[0]
sys.path.append(os.path.join(currentPath,'Muon-MCEq/Public/'))
```