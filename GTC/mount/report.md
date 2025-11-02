# 地形的方向性
目标：得到Eth（θ，φ）

## 地形数据源
ASTGTMV003_N22E114的dem地形数据  
找到的最好的分辨率30m*30m

## 各个厅的位置数据

经纬度：直接从 *Seasonal variation of the underground cosmic muon flux observed at Daya Bay* 图1估读  
海拔：从*The detector system of the Daya Bay reactor neutrino experiment*2.2节开头

> The rock overburden is 93 m at EH1, 100 m at EH2 and 324 m at EH3. Core samples taken throughout the area found the average rock density to be 2.6 g/cm3.

结合经纬度处所对应的地形高度反推，**存疑**

* EH1 E114.544  N22.6017  3m
* EH2 E114.55   N22.609   -42m
* EH3 E114.54   N22.616   -32m

## 算法（*有些小技巧*）

已知地形h(x,y),厅位置(x0,y0),对于一个角度（θ，φ）,求斜深度t(θ，φ)，利用动态步长往上走即可  
再利用*Gaisser*的(8.4)式 Emin=epsi*(exp(X/ξ)-1) 得到得到Eth（θ，φ）

## 结果

径向表示天顶角，中心为天顶  
角向表示方向角，上北下南左西右东

![pic1](/mount/res/EH1.png "EH1")
![pic2](/mount/res/EH2.png "EH3")
![pic3](/mount/res/EH3.png "EH3")