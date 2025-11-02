# 大气数据获取与处理
目标：得到T(x, y, h(或P),t)，进而得到ρ(X ,θ , φ, t)作为MCEq的输入

## 温度和重力势能数据源

ERA5数据
> https://cds.climate.copernicus.eu/  

有1940年至今的各个经纬度，大气压层（共47层，大约海拔均分）的温度  
精确到30km*30km，1h  
但是最小的气压层到1hPa，即大约50km，够用, 其上的所有在X变量中也仅有至多一个点  
！[pic0](/atmos/ERA5/res/P-H.png "P-H")

数据例如
！[pic1](/atmos/ERA5/res/10hPa.png "10hPa")
！[pic2](/atmos/ERA5/res/100hPa.png "100hPa")
！[pic3](/atmos/ERA5/res/1000hPa.png "1000hPa")


## 算法（*有些小技巧*）

对于每两层大气压层之间，采用动态步长斜向“攀爬”  
认为气压直接决定垂直厚度，即P=Xv*g,再用上学期得到的F(θ，T)取代cosθ，得到X  
“攀爬”过程的海拔变化采用Gaisser的(5.53)近似，即h=lcosθ + l^2/RE * (sinθ)^ 的微分形式

## 结果

！[pic4](/atmos/ERA5/res/res.png "res")