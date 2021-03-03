---
layout: post
title: 漫谈 C++ 移动语义系列--复制还是移动？
---
# Rambling about C++ Move Semantics Series--Copy or Move？

其一<br>

The first<br>
> 找到一样你所钟爱的事物，然后永不放手。 --小熊维尼

> Find thing you love and strick with it. --Winnie The Pooh

其二<br>

The second<br>
> 最终，小熊维尼还是失去了所有的蜂蜜。 --小熊维尼

> Eventually Winnie the Pooh lost all the honey. --Winnie The Pooh

其三<br>

The third<br>
> 我爱蜂蜜，但有时我希望蜜蜂能分享更多。 --小熊维尼

> I love honey，but sometimes I wish bees would share more. --Winnie The Pooh


其四<br>

The fourth<br>
> 最难的部分是留下的东西，……是时候放手了。 --小熊维尼

> The hardest part is what to leave behind,...It's time to let go.  --Winnie The Pooh

让我们从 C++11 之前谈起……<br>

Let's start before C++11...<br>

## 一、复制的一个例子（移动语义之前的世界）<br>
&emsp;&emsp;下面展示 *C++03* 世界里面的一个例子：<br>

&emsp;&emsp;The following shows a program from the *C++03* world：<br>

``` c++
#include <string>
#include <vector>

std::vector<std::string> getVector()
{
  std::vector<std::string> vec;
  vec.reserve(3);
  std::string longstr = "Long string to avoid small string optimization";
  vec.push_back(longstr);
  vec.push_back(longstr + longstr);
  vec.push_back(longstr);
  return vec;
}

int main(int argc, char* argv[])
{
  std::vector<std::string> cpvec;
  cpvec = getVector();
  return 0;
}

```
&emsp;&emsp;速览一下代码，让我们采用可视化堆和栈的方式来逐步分析这个程序。<br>

&emsp;&emsp;Take a quick look at the code and then let's analyze the program step by step using visual heap and stack.<br>

&emsp;&emsp;在开始分析之前，需要解释一下我们在示例里要选择如此长的字符串，原因就像字符串本身所表达的一样（狗头）。在优化机制的作用下，长度过于短小的字符串会被保存栈中，长度较长的字符串在会被保存在堆中，这种优化被称为*SSO*（*Small String Optimization*）。值得一提的是，这种优化并不一定会发生，这类话题会在后续其他系列文章中讨论。以下分析均基于 *SSO* 不会发生的时候。<br>

&emsp;&emsp;Before starting the analysis, it is necessary to explain that we have chosen such a long string in the example, simply for the same reason as expressed in the string itself. This optimization is called SSO (Small String Optimization), and it is worth mentioning that this optimization does not always happen, as will be discussed in other articles in this series. The following analysis is based on when SSO does not happen.<br>

&emsp;&emsp;首先，让我们从*main*函数开始读起，在*main*函数的第一句我们创建了一个空的vector *cpvec*：<br>

&emsp;&emsp;First, let's start reading from the *main* function. In the first sentence of the *main* function we create an empty vector cpvec.<br>
```
  std::vector<std::string> cpvec;
```
&emsp;&emsp;我们在栈上创建了一个vector对象，这个对象中没有任何元素，自然的，也没有元素分配任何内存，所以堆上是空的。如下图所示，所有的变量均被列出。<br>

&emsp;&emsp;We create a vector object on the stack, which does not have any elements in it and, naturally, no elements are allocated any memory, so the heap is empty. As shown in the figure below, all the variables are listed here.<br>

![_config.yml]({{ site.baseurl }}/images/copy/step0.png)

&emsp;&emsp;接下来，让我们考察*main*函数的第二条语句<br>

&emsp;&emsp;Next, let's explore the second statement of the *main* function，<br>

```
  cpvec = getVector();
```

&emsp;&emsp;在 *getVector()* 中，我们创建了一个vector，并为其在堆上分配三个元素的空间。需要注意的是，这次分配的内存未被初始化，拥有元素的数量依然是0。<br>

&emsp;&emsp;In *getVector()*, we create a vector and allocate space for it with three elements on the heap. Note that the memory allocated this time is not initialized and the number of elements owned remains 0.<br>

```
  std::vector<std::string> vec;
  vec.reserve(3);
```

![_config.yml]({{ site.baseurl }}/images/copy/step1.png)

&emsp;&emsp;接下来，创建一个字符串并使用“Long string to avoid small string optimization”初始化。<br>

&emsp;&emsp;Next, create a string and initialize it with "Long string to avoid small string optimization".<br>

```
  std::string longstr = "Long string to avoid small string optimization";
```
&emsp;&emsp;考虑到c_str()的存在，我们的字符串以'\0'结尾。在字符串创建的过程中，我们实质上是在栈上创建了一个对象，这个对象记录了字符串有46个字符，由于前文所述原因，SSO没有发生，我们在堆上创建了这个字符串，并在此对象中通过一个指针记录了指向这个字符串空间地址（string的实现原理类似于此，但并不完全相同，后续其它系列文章会对此作详细说明）。<br>

&emsp;&emsp;Considering the presence of c_str(), our string ends with '\0'. In the string creation process, we essentially create an object on the stack which records that the string has 46 characters, and for the reasons mentioned earlier, SSO does not happen, we create the string on the heap and record the address of the space pointing to this string in this object via a pointer (the implementation principle of string is similar, but not identical, and subsequent (other articles in the series will explain this in detail).<br>

![_config.yml]({{ site.baseurl }}/images/copy/Step2.png)

&emsp;&emsp;**C++标准库里面的所有容器都拥有值语义。** 接下来在解释分析下一步的同时来解释这句话。<br>

&emsp;&emsp;**All containers inside the C++ standard library have value semantics.** This statement is explained next while explaining the next step in the analysis.<br>

```
  vec.push_back(longstr);
```

&emsp;&emsp;值语义意味着传给push_back的参数是*longstr*的副本。也就是说，在这里我们对*longstr*进行了深拷贝，并用拷贝的副本来初始化vector的第一个元素。这里再次出现了一次内存的分配。在么有任何优化的情况下，当前我们在堆和栈中可以看到两个vector：*cpvec*和*vec*，两个string：*longstr*和位于vector第一个元素处的*longstr的副本*。如下图所示，这些对象互相独立，修改其中任意一个不会影响其它的对象的值，它们拥有独立的值存储空间。<br>

&emsp;&emsp;The value semantics means that the argument passed to push_back is a copy of *longstr*. That is, here we make a deep copy of *longstr* and initialize the first element of the vector with the copy, where an allocation of memory occurs again. In the absence of any optimization, we currently see two vectors in the heap and stack: *cpvec* and *vec*, and two strings: *longstr* and a *copy of longstr* at the first element of vectors. As shown in the figure below, these objects are independent of each other, and modifying any of them will not affect the values of the other objects, which have their own value storage space.<br>

![_config.yml]({{ site.baseurl }}/images/copy/step3.png)

&emsp;&emsp;下一步中，我们创建了一个临时的字符串*longstr+longstr*，之后将这个字符串插入到vector中，注意下图标红的位置，我们将按照此对象的产生、复制和销毁节点将其拆分为三步来讨论。<br>

&emsp;&emsp;In the next step, we create a temporary string *longstr+longstr* and later insert this string into the vector, note the position of the red marker below, which we will discuss by splitting this object into three steps according to its generation, copying and destruction nodes.<br>

```
  vec.push_back(longstr + longstr);
```

&emsp;&emsp;首先，创建一个长度为92的string，注意这个字符串是临时的。在值分类中，我们将其称为右值，这种值的特点是没有名称（为了方便描述，我们用这个表达式作为此值的名称）。如下图所示。<br>

&emsp;&emsp;First, create a string of length 92. Note that this string is temporary. In the value categories, we call it a rvalue, and this value is characterized by the absence of a name (for ease of description, we use this expression as the name of this value). This is shown in the figure below.<br>


![_config.yml]({{ site.baseurl }}/images/copy/Step4.png)

&emsp;&emsp;在这里再重复一遍，C++标准库里面的所有容器都拥有值语义，值语义意味着传给push_back的参数是一个副本。因此，对longstr+longstr拷贝和相关内存的分配是必不可少的。如下图所示，这时候堆和栈上我们可以看到两个vector，四个string：longstr和其副本以及longstr+longstr这个临时对象和它的副本。<br>

![_config.yml]({{ site.baseurl }}/images/copy/step5.png)

&emsp;&emsp;就像我们可爱的维尼小熊一样，抓住的蜂蜜最终也会失去，longstr+longstr在完成它的使命之后，便消失不见了。临时对象在它的生命周期结束之后，便会被销毁。仔细想来，这完全是没有必要的，如果蜜蜂们愿意分享他们的蜂蜜，或者我们的维尼小熊把蜂蜜交给合适的人，那这种浪费就不会发生。<br>

&emsp;&emsp;我们的临时对象longstr+longstr创建后被复制，复制后被销毁，这里复制和销毁相当的多余。用移动它到vector中代替创建+复制+销毁显然是一种很好的办法，但这在只有复制的世界里是没法做到的。那么我们能不能直接在vector里面直接原地构造呢？（这个问题留给阅读这篇文章的人）。如下图所示，在这条语句的末尾，这个临时变量被销毁了。<br>

![_config.yml]({{ site.baseurl }}/images/copy/step6.png)

&emsp;&emsp;接下来的语句和之前遇到的相同，拷贝和空间的分配也会继续发生，如下图所示。<br>

```
  vec.push_back(longstr);
```

![_config.yml]({{ site.baseurl }}/images/copy/step7.png)

&emsp;&emsp;我们可以注意到的不同点是，在此之后longstr不再会被使用。聪明一些的编译器可能会注意到这一点，用完整的搬动对象到vector代替拷贝对象到vector。但是，这种优化不总会发生，我们还是更关心一般的情况。我们假定这种不一定发生的优化一定不发生，这里复制依然会发生，销毁操作也会在longstr的生命周期结束的时候被销毁。和之前临时变量longstr+longstr一样，聪明的编译器也许会优化它，但这不一定会发生。<br>

&emsp;&emsp;这种开销在实时性要求极高的场景下有很大概率会成为整个软件系统的性能瓶颈。我们的系统工作的是否高效取决于编译器的心情，这样显然是说不过去的。在这种情况下，有一些十分诡异的言论蔓延开来，“在高性能场景中，使用C要比使用C++更好。”。这是一个很值得讨论的话题，但聊着聊着持反对和赞成观点的两拨人有可能会打起来，所以这个话题暂时打住。<br>

&emsp;&emsp;好的，我们继续对这个函数的最后一条语句进行讨论。<br>

```
  return vec;
```

&emsp;&emsp;和之前的分析不同，我们在这里考虑一种编译器的优化。这种优化是在标准中明确提及的，虽然不是强制要求，但大多数编译器都支持且会默认开启这种优化。<br>

&emsp;&emsp;在优化不存在时，在函数按值返回时，值的生命周期会自然结束。正常情况下，此值所对应的对象会被销毁，返回值是销毁值的副本。在上述例子中，我们必须对vec对象进行一次深拷贝，也就是说我们需要进行4次分配内存的操作（为vector返回值中的元素分配堆内存，并为三个字符串分配堆内存来容纳字符串内容）。<br>

&emsp;&emsp;当这种名为“具名返回值优化（NRVO）”的优化存在时，编译器生成代码，搬动vec到返回值。这样，复制便不会发生，看起来就像没有销毁vec，把它作为返回值来使用一样。值得注意的是，我们可以看到大多数编译器默认开启了这种优化。在按值返回的函数中，对函数内的具名（非临时）对象，复制这个值到返回值的操作并不会发生。如果我们在此对象的复制构造函数里面打印信息，是看不到复制构造函数被调用的。这种优化改变了程序原有的行为，没有人能完全确定这里会发生复制，但概率很大。我们可以说，在按值返回时，NRVO不一定会发生，但一般都会发生（狗头）。<br>

&emsp;&emsp;优化的存在与否决定了一些细微的东西。举例来说，对象longstr的销毁时机（也会受其他优化的影响）。<br>

&emsp;&emsp;如果优化没有发生，那么longstr会在return语句结束后销毁，而不是return语句完成时。<br>

![_config.yml]({{ site.baseurl }}/images/copy/step8.png)

&emsp;&emsp;如下图，为未开启优化时longstr销毁的时候。若开启了优化，则其销毁的时间点位于上图的return语句完成时（图中并未画出，是我懒了）。区别并不大，带来的副作用也是可控的。<br>

![_config.yml]({{ site.baseurl }}/images/copy/step9.png)

&emsp;&emsp;接下来，我们回到main函数里面（忽略getVector的红色标记，是我画错了，懒得改了，防剽窃专用错误）<br>

![_config.yml]({{ site.baseurl }}/images/copy/step10.png)

&emsp;&emsp;按照复制世界里赋值运算符的要求，修改左侧值的时候，右侧值不应该被修改。因此，复制操作不可避免，这里将返回值复制到了cpvec里。发生了4次分配内存的操作（分配vector一次，三个字符串各一次）。然后在语句结束的时候，返回值对象被立即销毁，过程如下图所示。<br>

![_config.yml]({{ site.baseurl }}/images/copy/step11.png)

&emsp;&emsp;这基本上就是关于复制的全部了。在*NRVO*开启的情况下，我们在这段程序中进行了10次内存分配和6次内存释放，做个减法，你会发现，我们实际上分配4次内存就可以了（狗头）。那么是哪些小调皮在捣鬼呢：<br>

- 总结之前的内容，显然临时变量复制是一条，插入临时变量到*vector*会导致1次不必要的分配和1次不必要的释放；<br>
- longstr不再使用时也发生了复制，需要插入vector且不再使用的值也导致了1次不必要的分配（这样说是因为它没有利用现有的longstr）和1次不必要的释放；<br>
- 返回值的再分配也导致了4次不必要的分配和4次不必要的释放。<br>

&emsp;&emsp;有人会说，你这种写法不是实践中常用的。通常我们会这样定义getVector：<br>

```
  void getVector(std::vector<std::string> &v);
```

&emsp;&emsp;或者我们可以使用std::vector提供的swap。<br>

```
getVector().swap(v);
```

&emsp;&emsp;抛开代码的美观程度不谈，因为我们可以采用更复杂的实现来让代码变得优美。这种写法仍然无法避免函数中插入临时变量时发生的不必要的分配和释放。<br>

&emsp;&emsp;做好准备，进入支持移动的C++11的时代。让我们看看，以上的问题如何被优雅的解决。<br>

## 二、移动的一个例子（移动语义的世界）<br>

&emsp;&emsp;下面的示例描述一段 C++11及以后的例子<br>

```
#include <string>
#include <vector>

std::vector<std::string> getVector()
{
  std::vector<std::string> vec;
  vec.reserve(3);
  std::string longstr = "Long string to avoid small string optimization";
  vec.push_back(longstr);
  vec.push_back(longstr + longstr);
  vec.push_back(std::move(longstr));
  return vec;
}

int main(int argc, char* argv[])
{
  std::vector<std::string> mvvec;
  mvvec = getVector();
  return 0;
}

```
&emsp;&emsp;在开始之前，我们假定事情可以按照我们的预期进行。在这之后，我来解释为何这样可以。<br>
&emsp;&emsp;我们的简单总结一下就是，**我们知道这个值是最后一次使用，那么我们应该窃取其内容（移动）**。<br>

&emsp;&emsp;和复制的例子一样，我们列出在所有非右值变量。<br>

![_config.yml]({{ site.baseurl }}/images/move/step0.png)

&emsp;&emsp;同样的，在getVector()我们创建了一个vector，并为其在堆上分配三个元素的空间。需要注意的是，这次分配的内存未被初始化，拥有元素的数量依然是0。<br>

```
  std::vector<std::string> vec;
  vec.reserve(3);
```
&emsp;&emsp;如下图所示：<br>

![_config.yml]({{ site.baseurl }}/images/move/setp1.png)

&emsp;&emsp;接下来，创建一个字符串并使用“Long string to avoid small string optimization”初始化。<br>

```
  std::string longstr = "Long string to avoid small string optimization";
```

![_config.yml]({{ site.baseurl }}/images/move/step2.png)

&emsp;&emsp;接下来我们看下一句。这里可以把longstr移动吗？显然不行。longstr会在构造longstr+longstr中使用，还会在vector的三个元素中被使用。进行移动是不合适的。因此这里仍然发生了复制。如下图所示：<br>

```
  vec.push_back(longstr);
```

&emsp;&emsp;这里我们在堆和栈上可以看到两个vector和两个string（longstr和它的副本，vector的元素之一）。<br>

![_config.yml]({{ site.baseurl }}/images/move/step3.png)

&emsp;&emsp;创建临时值*longstr+longstr*，并将临时值放入*vector*中。<br>

```
  vec.push_back(longstr + longstr);
```

&emsp;&emsp;不管是在复制的世界还是我们预想的世界，先构建*longstr+longstr*是不可绕过的一步，如下图所示。<br>

![_config.yml]({{ site.baseurl }}/images/move/step4.png)

&emsp;&emsp;因为longstr+longstr接下不会再次使用，我们从堆中偷取这个临时变量的内存，并让vector中第二个string元素内的指针指向它。<br>

&emsp;&emsp;在这里，我们拷贝了longstr+longstr的字符串长度值并将字符串长度置为0。longstr+longstr的指针地址也被复制并在复制完成后也被置空。这种拷贝的内容很少，通常为12-24个字节。注意，在这里我们并没有像NRVO一样，把堆上和栈上的空间一起偷走！！！这里是为了保证被偷对象的构造和析构函数成对执行。置0和置空保证了longstr+longstr析构函数可以正常执行。复制而不是移动栈上的值保证了vector的第二个元素在main函数退出时，它的析构函数也可以正常执行，所分配的内存能被正常释放。<br>

![_config.yml]({{ site.baseurl }}/images/move/step5.png)

&emsp;&emsp;接下来，我们调用临时对象的析构函数，释放其栈上的内存。被偷走内存由于不知道其地址和大小，因此被保留了下来。如下图所示，被偷走的内存未被释放。<br>

![_config.yml]({{ site.baseurl }}/images/move/step6.png)

&emsp;&emsp;接下来我们来看下面一句。仔细对比复制世界里的的个例子，我们发现其多出来了std::move。<br>

&emsp;&emsp;longstr的生命周期在函数返回时才会结束。对于编译器来说，要分析longstr是否为最后一次使用，我们需要分析使用这个值之后函数返回之前的所有内容。对于示例来说，这不需要太大的工作量。但是，如果遇到多层复杂的调用这个分析工作就会变得尤为棘手，通常也会给编写程序的人带来困惑和极大的挑战。<br>

&emsp;&emsp;我们如果能够告诉编译器，我们现在不需要这个值了，你可以把它的堆内存上的内容偷走，那么这个事情就简单多了。恰好，std::move就是来完成这个工作的。我们目前先不去说明这个move怎么实现，为什么这样实现可以达到效果（后续内容会展开解释这一点）。我们就明确的说，std::move可以告诉编译器可以偷走这个值。如下图所示<br>

```
  vec.push_back(std::move(longstr));
```

![_config.yml]({{ site.baseurl }}/images/move/step7.png)

&emsp;&emsp;同样的，这种偷走也只是偷走了堆上的内容，longstr发生的改变与longstr+longstr类似。在longstr的生命周期结束之前，longstr的状态成为了一个棘手的问题。**最难的部分是留下的东西**，临时变量longstr+longstr由于没有名字，我们在它被偷之后一定不能再次使用它。longstr由于存在名字，我们依然可以继续使用。这就要改string对象保持有效的状态，其析构函数经过中间其它方式使用之后也依然会被调用或被再次移动。我们需要保证的仅仅是string对象有效，其内部存储的字符串或长度我们可以不关心。但通常来说，清空长度是一种推荐的操作。我们可以说被移动的对象需要其生命周期结束之前保持一种“**有效但不确定状态**“。<br>

&emsp;&emsp;继续分析接下来的return语句，<br>

```
  return vec;
}
```
&emsp;&emsp;我们可以如法炮制的考虑NRVO，如果优化已经开启，直接偷走堆和栈上所有的东西，和复制的时候一样。<br>

&emsp;&emsp;如果优化没有开启，按照我们之前的设想，这个值不会在被使用，直接移走是否可行呢？答案是肯定的。编译器也可以很容易的知道这个值不再使用可以移动，代价也许就是小小的向前看一个花括号。这种判断在编译期就可以完成，中间涉及到的复制和前文所述一样，12或24字节，不能再多了。（狗头）<br>

![_config.yml]({{ site.baseurl }}/images/move/step8.png)

&emsp;&emsp;NRVO开启与不开启的差异留给读者分析。<br>

![_config.yml]({{ site.baseurl }}/images/move/step9.png)

&emsp;&emsp;最后，我们按照这种思路，分析下main函数内的赋值操作：<br>

```
  mvvec = getVector();
```

&emsp;&emsp;首先，无论是否开启NRVO，函数的返回值也和longstr+longstr一样，是一个临时值，不具有名字，所以这里的移动操作在优化未开启时会发生。在分号之前，移动后的临时变量也会保持“**有效但不确定状态**“。引入移动语义后，移动的分配操作符是自然而然可以存在的，我们可以透过偷取完成赋值的操作（注意移动语义和NRVO的区别）。<br>

![_config.yml]({{ site.baseurl }}/images/move/step10.png)

&emsp;&emsp;最后被偷取的返回值只在栈上留有内存，而这个内存也在其生命周期结束后被释放。<br>

![_config.yml]({{ site.baseurl }}/images/move/step11.png)

&emsp;&emsp;以上就是移动的所有内容，统计整个过程我们会发现，堆和栈内存的分配只发生了6次，其中2次为几乎不占内存的栈空间分配。<br>

&emsp;&emsp;总结一下，在移动的世界里，我们节省了那些不必要的内存分配和释放。<br>

- 临时对象的分配和释放（这在复制的世界里无法解决）<br>
- 我们可以通过std::move来指示那些对象不再需要，通过移动来偷取它。<br>
- 临时vector及其元素的分配。<br>

&emsp;&emsp;只有第二种情况需要我们指定，其余的优化在移动语义存在的世界中，自然而然地发生了。<br>

&emsp;&emsp;“在高性能场景中，使用C要比使用C++更好。”这是一个很值得讨论的话题在移动语义出现后的世界里，在默默的被改变着。<br>

&emsp;&emsp;下一篇，计划聊一聊“移动语义的实现”和文中多次提到的“**有效但不确定状态**“。敬请期待，感谢您的阅读，欢迎指出错误，我的联系方式详见blog下方。