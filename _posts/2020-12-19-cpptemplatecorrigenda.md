---
layout: post
title: C++ Templates 中文版勘误（持续更新）
---
### 说明 ###
&emsp;&emsp;本内容适用与陈伟柱译的《C++ Templates 中文版》，人民邮电出版社，ISBN&emsp;978-7-115-31281-5<br>
部分错误为英文原版第一版书籍也存在的错误，其它翻译版或原版可对照参考

### 勘误表 ###
#### 第1部分 基础 ####
##### 第3章 类模板 #####
***3.2 类模板 Stack 的使用***<br>
P26:<br>
> &emsp;&emsp;你可以像使用其他任何类型一样地使用实例化后的类模板类型（如 Stack< int>），**只要它支持所调用的操作就可以**：<br>

&emsp;&emsp;严格来说，这样表述才是正确的 实例化的类模板的类型可以与任何其他类型一样使用。可以使用 const 或 volatile对其进行限定，或者从中派生数组和引用类型。甚至可以在构建另一个模板类型时将其用作类型参数：
##### 第5章 技巧性基础知识 #####
***5.3 成员模板***、***5.4 模板的模板参数***
P43、P45、P49:<br>
> ```cpp
if ((void*) this == (void*)& op2) {　 //赋值给自身吗 
    return *this; 
}
```

&emsp;&emsp;此处判断是无用的。由于模板重载解析的问题，判断rsh==this没有必要，因为存在针对相同类型默认的模板成员赋值赋值运算符，则会被优先使用。赋值自身必然是交由默认的模板成员赋值运算符来完成的，不会使用这个模板赋值运算符。<br>
#### 第2部分 深入模板 ####
##### 第8章 深入模板基础 #####
***8.3.3 非类型实参***
P105、P07:<br>
> ```cpp
Public:
```

修正为：<br>
```cpp
public:
```
##### 第9章 模板中的名称 #####
***9.2.3 插入式类名称***
P122:<br>
> ```cpp
 C<void> b;
```

修改为：<br>
```cpp
C<void> *b;
```
&emsp;&emsp;原因：类不能递归定义，因为编译器在为具体的对象分配大小时必须知道其大小。<br>
P126:<br>
> 我们改写了（泛型的）Trap X<T>::x，

此处应该为：<br>
我们改写了（泛型的）Trap<T>::x，<br>
##### 第10章 实例化 #####
***10.3.4 跨翻译单元查找***
P147：对第二阶段查找的描述错误<br>
> &emsp;&emsp;第2阶段发生在产生 POI（实例化点）的时候。在这在这一点上，会使用普通查找规则**和 ADL 规则**来查找依赖型受限名称。

显然是错误的，ADL查找只能查找非受限名称，修改为<br>
&emsp;&emsp;第2阶段发生在产生 POI（实例化点）的时候。在这在这一点上，会使用普通查找规则来查找依赖型受限名称。<br>
##### 第11章 模板实参演绎 #####
***11.3 特殊的演绎情况***
P168代码：<br>
> ```cpp
 template<typename T, int N> operator T[N]&();
```

应该为：<br>
> ```cpp
 template<typename T, int N> operator T&();
```

P168代码错误引起的描述错误：<br>
> &emsp;&emsp;在此，我们试图把 S 转型为 int (&)[20]； 因此，类型 A 为 int[ 20]，而类型 P 为 **T[N]**。于是，用类型 **int** 替换 T，**用 20 替换 N 之后，**该演绎就是成功的。

修改为：<br>
&emsp;&emsp;在此，我们试图把 S 转型为 int (&)[20]； 因此，类型 A 为 int[ 20]，而类型 P 为 **T**。于是，用类型 **int[20]** 替换 T，该演绎就是成功的。<br>
#### 第3部分 模板与设计 ####
##### 第18章 表达式模板 #####
***18.2.5 表达式模板赋值***
P330:<br>
> ```cpp
template< typename T, typename R1, typename R2>
Array< T, A_ Subscript< T, R1, R2> > 
Array< T, R1>:: operator[] (Array< T, R2> const & b) { 
    return Array< T, A_ Subscript< T, R1, R2> > 
        (A_ Subscript< T, R1, R2>( this—> rep(), b. rep())); 
}
```

改进，从通用性的角度考虑，考虑隐式转换存在，修改如下:
```cpp
template<typename T,typename R>
tempate<typename T1,template R1> 
inline Array<T,A_Subscript<T,R,R1> > 
Array<T,R> :: operator[](Array<T1,R1> const& b）{ 
    return Array<T,A_Subscript<T,R,R1> >
        (A_Subscript<T,R,R1>(this->rep(),b->rep())); 
}
```
#### 第4部分 高级应用程序 ####
##### 第20章 智能指针 #####
***20.2.8 隐式转型***
P380:<br>
> ```cpp
class CountingPtr; friend
```

修改为：<br>
```cpp
friend class CountingPtr;
```



