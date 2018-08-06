# bilibili_downloader
## 1. 简介
出于个人兴趣爱好，随便写的一个bilibili批量下载工具，可以批量下载指定合集或者指定up主的全部视频，也可以忽略其中某些不感兴趣的视频
功能很弱鸡，代码很垃圾，一定有BUG，如果有发现BUG，尽管提Issue，反正也不会修，这辈子都不会修BUG。。。

## 2. 环境依赖
1. Linux环境下编译通过，Windows环境没试过，应该可以吧。。。    
2. Python3   
3. you-get 必须要有you-get！！！在此感谢you-get作者和api作者

## 3. 前置准备
### 3.1.准备好登录B站的cookies/headers等，
需要手动修改`get_up_vlist`方法
### 3.2.准备好要下载的视频av号
填入bilibili.xlsx 'aid'sheet中，一行一个，title、author等不用填，脚本会自动产生  
### 3.3.准备好要批量下载的up主用户id（进入其主页查看），
填入bilibili.xlsx 'mid'sheet中，记得填enable，一行一个，一样，多余信息不用填   

## 4.运行脚本

### 4.1 产生download list
`./gen_download_cmd.py --gen_download_list`  
遍历aid、mid sheet 完成初始化设置，同时产生以下文件
`download.json`文件供下一条指令使用   
`aid_done.list`用来保存已下载的单独视频aid   
`cid_done.list`用来保存已下载的分P视频cid    

如果不是第一次执行，且已经下载完成一部分视频，建议加上`--enable_skip`选项，可以避免重复提交api请求  

### 4.2 执行下载
如检查download.json确实如预期，则执行  
`./gen_download_cmd.py --enable_download`

### 4.3 检查进度
脚本在下载过程中会实时更新`download.list`文件，可以通过查看该文件获得当前下载进度

### 4.4 忽略不感兴趣的视频
在4.1执行后，如有不感兴趣的视频，可以在对应的flag 列填入OFF或者什么都不填来跳过
