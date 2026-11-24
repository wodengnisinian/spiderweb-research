# AI理解：定义、机制与证据边界的原始文献资料

日期：2026-11-05。这里只整理资料，不训练、不改模型、不把调研自动转成下一轮实验。下面8条均实际在线检索并读取原始论文页面或原文片段；具体阅读范围与访问失败记录见 `ai_sources.json`。这是一组针对问题的精选来源，不是当前全部AI能力的穷尽综述。

## 资料支持的主要区分

**自注意力是信息交互机制，理解是需要定义和证据支持的能力主张。**原始Transformer规定向量如何按内容混合，训练部分另外规定翻译数据与优化过程。仅知道架构，无法推出它学过什么、采用哪种规则或是否理解某个具体问题。[Vaswani等2017](https://arxiv.org/abs/1706.03762)。

**“理解”争论的一部分来自定义不同。**Bender与Koller把语言意义连到交际意图，Harnad追问符号如何具有系统可用的内容，Bisk等强调感知、行动与社会共享情境。这些要求比“识别两个句子是否同义”更广。它们是需要认真对待的理论立场，不应伪装成对一切现代模型的通用实验证伪。[Bender与Koller2020](https://aclanthology.org/2020.acl-main.463/)、[Harnad1990](https://www.southampton.ac.uk/~harnad/Papers/Harnad/harnad90.sgproblem.html)、[Bisk等2020](https://aclanthology.org/2020.emnlp-main.703/)。

**缺乏直接感知，也不等于学不到任何世界结构。**颜色研究发现文本表征与感知空间有一定结构对应，说明人类经验可以在语言中留下可学习线索。但颜色结构对应没有证明视觉体验、全面接地或通用理解。它与更严格的交际意义定义不必是在回答同一个问题。[Abdou等2021](https://aclanthology.org/2021.conll-1.9/)。

**正确行为、可读出表示、模型实际使用表示，是不同层次的证据。**HANS说明行为得分可能混有启发式；探针控制任务说明信息可能由读出器自身学会；捷径综述提醒不要把数据集分数直接当成底层能力。局部失败也需要结合训练拟合与任务条件，不能扩张为“自注意力原理上不可能理解”。[McCoy等2019](https://aclanthology.org/P19-1334/)、[Hewitt与Liang2019](https://aclanthology.org/D19-1275/)、[Geirhos等2020](https://www.nature.com/articles/s42256-020-00257-z)。

## 八条精选来源及其具体用途

1. **Vaswani等，2017，实验：**[Attention Is All You Need](https://arxiv.org/abs/1706.03762)。读取官方HTML注意力与训练段落。它给出查询/键/值计算和完整Transformer结构，实证对象是翻译与句法分析。可用于解释“怎样整合上下文”；不支持“有注意力就会理解”。数学中的Q也不是自然语言问题意图的同义词。

2. **Bender与Koller，2020，理论：**[Climbing towards NLU](https://aclanthology.org/2020.acl-main.463/)。读取工作定义及其对语义相似度和BERT的讨论。作者以形式与交际意图的关系定义意义，据此批评只靠形式的学习。应把它作为有前提的论证阅读，不能只摘一句变成现代所有AI均无理解的结论。

3. **Harnad，1990，理论：**[The Symbol Grounding Problem](https://www.southampton.ac.uk/~harnad/Papers/Harnad/harnad90.sgproblem.html)。读取作者托管原文摘要和候选方案。核心是符号意义如何不只依赖外部解释者。感觉/类别表征是作者候选方案；本文不证明机器人硬件是所有理解的必要条件。

4. **Bisk等，2020，理论与研究路线：**[Experience Grounds Language](https://aclanthology.org/2020.emnlp-main.703/)。读取World Scope定义与社会互动片段。指出可用经验包括文字、感知、行动与共享社会背景。五类Scope是分析视角，不是已经验证的智能等级或“加一种模态就理解”的工程保证。

5. **McCoy等，2019，实验：**[Right for the Wrong Reasons／HANS](https://aclanthology.org/P19-1334/)。读取原文启发式、数据偏差与诊断段落。词重合、子序列或成分启发式可以在常规NLI评测成功，却在控制题失败；原文也记录部分训练改善。它说明需要限定行为解释，不能代表当前所有AI或中文。

6. **Hewitt与Liang，2019，实验：**[Designing and Interpreting Probes with Control Tasks](https://aclanthology.org/D19-1275/)。读取官方摘要及PDF第一页，后续定位请求超时。控制任务限制探针自身记忆带来的解释混淆。即便可读出信息，主模型是否使用仍是额外问题；探针不是通用理解检测器。

7. **Geirhos等，2020，综述/Perspective：**[Shortcut Learning in Deep Neural Networks](https://www.nature.com/articles/s42256-020-00257-z)，另读可访问的[作者arXiv正文](https://arxiv.org/html/2004.07780v5)。区分训练拟合、IID解法和预期解法，提醒分数与能力的关系。它不允许把每次分布外失败都未经分析归为捷径。

8. **Abdou等，2021，实验：**[Can Language Models Encode Perceptual Structure Without Grounding?](https://aclanthology.org/2021.conll-1.9/)。读取原始PDF摘要、引言及方法开头。发现颜色词表示与CIELAB空间有显著对应；简单共现也能承载部分信号。它是某类世界结构可从语言中学得的正面证据，仍限于颜色表示分析，没有证明全面理解或因果使用。

## 对“理解一个问题”可以怎样说得更准确

以下是整理者结合文献给出的区分，不是宣称学界已有统一定义：

- **语言内容：**问到哪些人、事、关系、条件、否定和未知项。形式相近不等于内容相同，内容判断也不等于给出了正确事实答案。
- **指称与情境：**“这里”“它”“刚才那个”指向什么；问题在什么环境和已有知识下提出。孤立文本可能没有充分信息。
- **交际目的：**对方是在问信息、确认、质疑、请求行动，还是暗示别的事。只按字面命题处理可能不足以确定。
- **证据范围：**某次任务做对、跨表达稳定、表示可读出、行为因语义改变而恰当改变，各能支持不同强度的主张。

同义二分类覆盖其中一小部分，是行为任务，不等于一个系统能够对单个问题作出独立解释、识别现实所指、把握交际目的或迁移到所有问题。反过来，一个小模型在有限训练下失败，也不能单独否定更广泛模型具有相关能力。

这些资料的共同价值是让“它理解了什么、依据是什么、还有什么没有测到”变得具体，而不是替所有AI作一次性的能／不能理解裁决。本次资料收集到此为止，不据此自动安排训练或算法变更。
