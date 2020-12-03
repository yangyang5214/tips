# tips
 
运行在树莓派，手下留情。。。

base_url: http://116.232.10.46:8700 

IP 可能会变，下列的 ip 不更新。

域名不变（https://www.hexianwei.com/api） update: 2020-12-03

### 小知识点

> 每次 LOL 的时候，都会出现小贴士，也就是一些 LOL 的小知识

随机返回一条知识点

```
curl http://116.232.10.46:8700/tips
``` 
### img

|   type | source |
| :---: |   :---: |
|   0    |  必应      |
|   1    |  keep      |
|   >1    |  知乎      |


```
curl http://116.232.10.46:8700/img?type=0
curl http://116.232.10.46:8700/img?type=1
```

### jrebel


https://jrebel.hexianwei.com/88262a39-9448-4da5-b368-15e4d2549666


jrebel 激活码，代理 lanyu 的服务


### url parse

处理爬虫的时候，看请求不太方便，所以做了这个工具。解析长 url 的参数。

![](https://beer-1256523277.cos.ap-shanghai.myqcloud.com/blog/20201203082856.png)



### 同步文件工具


本地的一个文件夹，同步到远程服务器。


只支持 本地 -> 远程，不支持双向。本来打算写的是双向的，但是，问题很多，并没有那么容易。涉及到多人更改的话，git 都还要处理冲突呢。。。

https://github.com/yangyang5214/tips/blob/main/sync_cloud.py

设置个 cron job  就好了，每 5 分钟跑一次。

```
*/5 * * * * python /Users/bieyang/sh/sync_cloud.py
```

基本步骤：

1. 备份上次的快照文件
2. 生成最新的快照文件
3. 对比，如果有文件删除，则删除远程（假删除，设置为隐藏文件）
4. 对比，如果有文件更新，则上传到远程

