---
layout: post
title: Spy++ for Qt 开发笔记——如何监控 QObject 对象的销毁与创建（一）
---
### 说明 ###
&emsp;&emsp;本内容适合熟悉 C++ 、有 Qt (https://qt.io) 使用经验或者特殊使用需求的同学使用，欢迎批评指正。（实验性工作）

### 概述 ###
&emsp;&emsp;本系列是我一直计划去做的一个调试工具，计划了这么久终于找到时间开工了，工程量估计会十分巨大，做个记录很有必要。
产生这个计划的原因有以下三点
1. Qt 在官方并没有提供特别好用的运行时界面调试工具；
2. Qt 界面的句柄通过 spy++ 只能获取到最顶层的主窗口举报而看不到窗口（除非使用 winid 进行处理，而 winid 会带来很多样式问题）；
3. 我希望我能够在无代码或不方便使用代码调试的环境下观察程序的信号-槽的触发过程、Qt 消息的触发过程、在运行时查看及修改样式及控件属性、QML的运行时编辑、网络远程调试以及崩溃时操作信息记录。

&emsp;&emsp;实验性的工作会做详细记录，说明处会有备注。


### 大致规划 ###
&emsp;&emsp;在正式开工前以需要突破点为入口，实验性内容为主，后续会增加关于具体开发的一些内容。
### 局限 ###
&emsp;&emsp;一些内容受 Qt 版本的影响，不同版本之间实现会存在差异，目前使用版本为 Qt 5.8.0。
### 为什么要监控 QObject 的创建与销毁 ###
&emsp;&emsp;Qt 的大部分界面功能实现都继承自类 QObject，窗体的构建首先创建的是 QObject，监控 QObject的变化就可以间接的监控窗口控件的变化。
### 思路 ###
&emsp;&emsp;阅读 QObject 构造析构函数寻找灵感 https://github.com/qt/qtbase/blob/5.8/src/corelib/kernel/qobject.cpp
构造函数：
```cpp
QObject::QObject(...)
    : d_ptr(...)
{
...
    if (Q_UNLIKELY(qtHookData[QHooks::AddQObject]))
        reinterpret_cast<QHooks::AddQObjectCallback>(qtHookData[QHooks::AddQObject])(this);
}
```
析构函数：
```cpp
QObject::~QObject()
{
...
    if (Q_UNLIKELY(qtHookData[QHooks::RemoveQObject]))
        reinterpret_cast<QHooks::RemoveQObjectCallback>(qtHookData[QHooks::RemoveQObject])(this);
...
}
```
每当执行构造函数时 qtHookData[QHooks::AddQObject] 指向的回调会被执行，执行析构函数时 qtHookData[QHooks::RemoveQObject] 指向的回调函数会被执行，因此我们使用替换回调函数为我们自己的监控函数即可做到记录 QObject 对象的销毁与创建的效果。需要注意的是我们需要保存原有的回调，在完成我们这些记录操作后，执行原来的回调。

### 实现逻辑 ###
大致实现逻辑如下
```cpp
#include<private/qhooks_p.h>
static void (*orgin_startup_hook)() = nullptr;
static void (*orgin_addObject)(QObject *) = nullptr;
static void (*orgin_removeObject)(QObject *) = nullptr;

extern "C"{
extern void custom_startup_hook_callback();
extern void custom_addObject_hook_callback(QObject *obj);
extern void custom_removeObject_hook_callback(QObject *obj);
extern void install_hook();
}

bool hooksInstalled()
{
    return qtHookData[QHooks::AddQObject] == reinterpret_cast<quintptr>(&custom_addObject_hook_callback);
}

extern "C" void custom_startup_hook_callback()
{
	//这里实现监控逻辑
	//判断是否需要处理原始回调
    if (orgin_startup_hook)
        orgin_startup_hook();
}

extern "C"  void custom_addObject_hook_callback(QObject *obj)
{
	//这里实现创建操作的监控逻辑
	//判断是否需要处理原始回调
    if (orgin_addObject)
    {
        orgin_addObject(obj);
    }
}

extern "C" void custom_removeObject_hook_callback(QObject *obj)
{
    //这里实现销毁操作监控逻辑
	//判断是否需要处理原始回调
    if (orgin_removeObject)
    {
        orgin_removeObject(obj);
    }
}

static void installQHooks()
{
	//保存原来的回调
    orgin_addObject
            = reinterpret_cast<QHooks::AddQObjectCallback>(qtHookData[QHooks::AddQObject]);
    orgin_removeObject
            = reinterpret_cast<QHooks::RemoveQObjectCallback>(qtHookData[QHooks::RemoveQObject]);
    orgin_startup_hook
            = reinterpret_cast<QHooks::StartupCallback>(qtHookData[QHooks::Startup]);
	//使用自定义的回调
    qtHookData[QHooks::Startup] = reinterpret_cast<quintptr>(&custom_startup_hook_callback);
    qtHookData[QHooks::AddQObject] = reinterpret_cast<quintptr>(&custom_addObject_hook_callback);
    qtHookData[QHooks::RemoveQObject] = reinterpret_cast<quintptr>(&custom_removeObject_hook_callback);
}

static void install_hook()
{
    if(hooksInstalled())
        return;
    installQHooks();
}
```
### 一些细节 ###
使用private/qhooks_p.h需包含以下头文件查找目录
```
$(QTDIR)/include/QtCore/5.8.0/QtCore
$(QTDIR)/include/QtCore/5.8.0
```
### 没有提到的内容 ###
以下这些内容会在后面的文章里面提到，欢迎继续关注
1. hook安装的时机；
2. 如何保证跨线程访问下的安全性；
3. 监控操作的具体实现