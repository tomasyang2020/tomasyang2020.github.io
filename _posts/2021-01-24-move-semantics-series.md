---
layout: post
title: 漫谈C++移动语义系列（目录）
---
### 前情提要 ###
### Previously on Move Semantics ###
&emsp;&emsp;漫谈移动语义系列是我在重新学习现代 C++ 后有关值系统相关应用的一些概要记录、理解与个人感想，为了防止时间长了忘记，计划总结写下本系列作为备忘。希望本备忘能给在学习这块的朋友们带来一些有益的帮助。<br>
&emsp;&emsp;The Rambling on Move Semantics series is a summary record, understanding and personal feelings about the value system application after I relearned modern C++, in order to prevent forgetting it after a long time, I plan to summarize and write this series as a memo. I hope this memo can give some useful help to those who are learning this part.<br>
&emsp;&emsp;最近在看一些有关编程语言所有权有关的一些内容，想起来现代的 C++ 也在所有权方面做了许多改进，因此开始重温现代 C++ 的一些内容，可以说是重新开始学 C++ 。这次重新学习的不同点是主要的参考资料来源是各版本的 C++ 标准草案（正式版本有点贵）及一些归入标准前的一些提案，以 C++11 为界限，来了解C++ 这门编程语言在其借鉴了多种语言特性之后的发展和变化。这块也包含了实际工程活动中三种使用 C++ 的方式，面向对象、函数式和模板元。<br>
&emsp;&emsp;Recently, I was reading some content about the ownership of programming languages, and I realized that modern C++ has also made many improvements in ownership, so I started to revisit some of the contents of modern C++, so to speak, I started to learn C++ again. The difference in this re-learning is that the main source of reference is the draft C++ standard (the official version is a bit expensive) and some of the pre-standard proposals, using C++11 as a boundary to understand how C++ has evolved and changed as a programming language, drawing on the features of many languages. This section also covers three ways of using C++ in practical engineering activities, object-oriented, functional, and meta-template.<br>
&emsp;&emsp;本系列主要讨论移动语义存在的意义、移动语义和拷贝语义的对比、移动语义给C++带来的变化、移动与拷贝的特殊函数对类的影响以及移动语义在现代C++编程中的应用。对示例主要会使用到面向对象和模板元的方式，函数式的方式在本块也会有所提及，另外“重载决议”相关的内容也会在这里有所涉及。<br>
&emsp;&emsp;This series focuses on the meaning of the existence of move semantics, the comparison of move semantics and copy semantics, the changes brought to C++ by move semantics, the impact of special functions of move and copy on classes, and the application of move semantics in modern C++ programming. Object-oriented and template-based approaches will be used for the examples, and functional approaches will be mentioned in this section, as well as "overloading resolutions".<br>
### 目录 ###
### Contents ###

待更新<br>
TO-DO<br>
