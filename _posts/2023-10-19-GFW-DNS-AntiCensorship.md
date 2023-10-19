---
layout: post
title: 防止某入侵检测系统DNS污染的方法（POC篇）
---

### 声明 ###
&emsp;&emsp;本文描述的技术可能具有时效性，文章内容仅供相关领域人员研讨学习。本文适用于中国大陆地区的网络环境，对笔者所在区域所使用的运营商所部署的 GFW 设备有效。可能在其他地区无效/经过一定修改后才有效。
### DNS 查询（UDP） ###
```bash
dig v2ex.com @8.8.8.8
```
&emsp;&emsp;通过抓包可以明显看到有 DNS 抢答的现象，最后一个包是正确的（PS。也有可能只有抢答包）

![_config.yml]({{ site.baseurl }}/images/dns-anti-censorship/udp-dig.png)

POC如下
```bash
echo -en '\x39\x21\x01\x20\x00\x01\x00\x00\x00\x00\x00\x01\xc0\x29\x00\x01\x00\x01\x00\x00\x29\x10\x00\x00\x00\x00\x00\x00\x0c\x00\x0a\x00\x08\xd9\x68\x98\x35\xdb\x07\xd2\x62\x04\x76\x32\x65\x78\xc0\x30\xc0\x32\xc0\x34\xc0\x36\xc0\x38\xc0\x3a\xc0\x3c\xc0\x3e\xc0\x40\xc0\x42\xc0\x44\xc0\x46\xc0\x48\xc0\x4a\xc0\x4c\xc0\x4e\xc0\x50\x03\x63\x6f\x6d\x00' | nc -u -w2 8.8.8.8 53 | hd
```
POC输出如下
```bash
00000000  39 21 81 a0 00 01 00 03  00 00 00 01 04 76 32 65  |9!...........v2e|
00000010  78 03 63 6f 6d 00 00 01  00 01 c0 0c 00 01 00 01  |x.com...........|
00000020  00 00 01 17 00 04 68 14  0a da c0 0c 00 01 00 01  |......h.........|
00000030  00 00 01 17 00 04 68 14  09 da c0 0c 00 01 00 01  |......h.........|
00000040  00 00 01 17 00 04 ac 43  03 bc 00 00 29 02 00 00  |.......C....)...|
00000050  00 00 00 00 00                                    |.....|
00000055
```
&emsp;&emsp;抓包可以看到完全没有抢答


![_config.yml]({{ site.baseurl }}/images/dns-anti-censorship/udp-poc.png)


### DNS 查询（TCP） ###
```bash
dig +tcp v2ex.com @8.8.8.8
```
&emsp;&emsp;可以看到查询后直接被 RST 

![_config.yml]({{ site.baseurl }}/images/dns-anti-censorship/tcp-dig.png)

POC如下
```bash
echo -en '\x00\x55\x39\x21\x01\x20\x00\x01\x00\x00\x00\x00\x00\x01\xc0\x29\x00\x01\x00\x01\x00\x00\x29\x10\x00\x00\x00\x00\x00\x00\x0c\x00\x0a\x00\x08\xd9\x68\x98\x35\xdb\x07\xd2\x62\x04\x76\x32\x65\x78\xc0\x30\xc0\x32\xc0\x34\xc0\x36\xc0\x38\xc0\x3a\xc0\x3c\xc0\x3e\xc0\x40\xc0\x42\xc0\x44\xc0\x46\xc0\x48\xc0\x4a\xc0\x4c\xc0\x4e\xc0\x50\x03\x63\x6f\x6d\x00' | nc -q1 8.8.8.8 53 | hd```
POC输出如下
```bash
00000000  00 55 39 21 81 a0 00 01  00 03 00 00 00 01 04 76  |.U9!...........v|
00000010  32 65 78 03 63 6f 6d 00  00 01 00 01 c0 0c 00 01  |2ex.com.........|
00000020  00 01 00 00 01 2c 00 04  68 14 0a da c0 0c 00 01  |.....,..h.......|
00000030  00 01 00 00 01 2c 00 04  68 14 09 da c0 0c 00 01  |.....,..h.......|
00000040  00 01 00 00 01 2c 00 04  ac 43 03 bc 00 00 29 02  |.....,...C....).|
00000050  00 00 00 00 00 00 00                              |.......|
00000057
```
&emsp;&emsp;抓包可以看到完全没有抢答

![_config.yml]({{ site.baseurl }}/images/dns-anti-censorship/tcp-poc.png)

### 原理 ###
&emsp;&emsp;可以看到，仿佛 GFW 没有看到这些包一样，这是为什么呢？原理篇做说明，懂的人抓包一看就懂
