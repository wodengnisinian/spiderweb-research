# 语言模型的递归、状态空间与注意力架构对照

日期：2026-11-05。本资料是九张**抽样架构卡**，不是2026最新模型穷尽清单。卡片中的版本、训练目标、公开程度和实际读取范围见 alternative_models.json。只读原论文与官方资料，没有训练、运行模型或修改旧实验。

## 首先看历史信息放在哪里

| 卡片 | 指定版本 | 跨位置的信息如何传递 | softmax自注意力的位置 |
|---|---|---|---|
| ALT01 LSTM | 1997原始；另标1999/2000遗忘门扩展 | c记忆与h输出逐步递推 | 原生循环路线，不是Transformer删一个模块 |
| ALT02 GRU | Cho等2014 | 更新/重置门控制固定维h | 原始双RNN没有全历史self-attention |
| ALT03 Mamba | Mamba-1/S6 | 输入相关SSM状态，短卷积缓存 | 纯Mamba以selective SSM混合token |
| ALT04 Mamba-2 | SSD与2024原块 | 块内矩阵计算、块间有限状态 | 纯版SSD；论文hybrid另加attention |
| ALT05 RWKV-7 | 2025 Goose | 广义delta矩阵状态加token shift | 非标准softmax历史读出 |
| ALT06 RetNet | 2023原始multi-scale retention | 衰减键值状态，可递归/并行/分块计算 | retention替换attention，FFN仍在 |
| ALT07 Gated DeltaNet | 2024v1/ICLR2025 | 遗忘门加key方向纠错式矩阵更新 | 纯版替换attention；H1/H2含滑窗attention |
| ALT08 BERT | 原始Base/Large | 每层保留全输入token矩阵，双向交互 | encoder-only dense attention对照 |
| ALT09 T5 | 原始2019/2020 | encoder全输入表征＋decoder输出前缀/cross-attention | encoder–decoder dense attention对照 |

原始入口：[LSTM](https://doi.org/10.1162/neco.1997.9.8.1735)、[GRU](https://aclanthology.org/D14-1179.pdf)、[Mamba](https://arxiv.org/html/2312.00752v2)、[Mamba-2](https://arxiv.org/html/2405.21060v1)、[RWKV-7](https://arxiv.org/html/2503.14456v1)、[RetNet](https://arxiv.org/html/2307.08621v4)、[Gated DeltaNet](https://arxiv.org/html/2412.06464v1)、[BERT](https://aclanthology.org/N19-1423.pdf)、[T5](https://jmlr.org/papers/volume21/20-074/20-074.pdf)。

这里最清楚的一条轴是：每次通过有限状态汇总历史，还是保留较多逐位置表征供后续读取。有限状态不等于只能记很短；保留历史token也不等于保证正确使用所有信息。两者都要靠训练形成可用表示，且有状态容量、数值、计算和数据等条件。

## 架构与训练目标是两件事

LSTM、GRU、SSM、delta更新首先定义信息如何流动。它们可以配语言建模、分类或其他目标，并没有一个门控公式直接等于“理解损失”。BERT原始MLM＋NSP和T5的span corruption/text-to-text也属于训练任务选择；encoder-only、encoder–decoder及其注意力可见范围属于结构选择。[GRU原文](https://aclanthology.org/D14-1179.pdf)、[BERT原文](https://aclanthology.org/N19-1423.pdf)、[T5原文](https://jmlr.org/papers/volume21/20-074/20-074.pdf)

RWKV-7或Gated DeltaNet中的在线学习解释，主要描述**本次上下文里的状态更新**；不能仅凭这个名称说推理时会对所有持久网络参数做常规反向传播。语言建模训练仍须另行说明。[RWKV-7](https://arxiv.org/html/2503.14456v1)、[Gated DeltaNet](https://arxiv.org/html/2412.06464v1)

## 复杂度需要说明在对什么变量计数

若固定层数、宽度、head与状态维，循环模型单步推理的状态与工作量可以相对历史长度T不增长，但这个常数可能包含矩阵状态；改变状态宽度，成本就会变。对长度T完整处理仍需至少消费T个token，训练还要存储、分块或重算中间激活。

RetNet同一机制的朴素parallel形式含T×T项，recurrent形式则使用有限状态；不能把“支持并行”与“所有训练方式均线性”混为一谈。[RetNet](https://arxiv.org/html/2307.08621v4)

Mamba-2论文的SSD是特定结构下的对偶与算法，不是“任意softmax Transformer等价任意SSM”。其内核速度比较也不是整个模型、所有长度和硬件的普遍速度倍数。[Mamba-2](https://arxiv.org/html/2405.21060v1)

BERT/T5的普通dense attention交互对序列长度具有二次项；这不意味着每个优化实现都要在显存中物化完整注意力矩阵，也不意味着FFN/投影的宽度成本可以省略。

## 避免把版本与公开证据拼错

- 1997 LSTM与后来加入遗忘门的常见LSTM不能共用一张未注明版本的三门图。GRU公式也要核对reset在矩阵乘前后的位置。
- RWKV-7是Goose，不是RWKV-6 Finch。部分World权重由早期checkpoint升级，训练数据量应看完整历史；不能只比较最后一段续训。
- RetNet原版与2024 Gated RetNet/YOCO不同；官方repo还记录了数值/归一化修复。
- 纯Mamba-2/Gated DeltaNet与含attention混合版分别登记；不能把混合版收益全归给“完全取消attention”。
- 原始T5、T5.1.1、Flan-T5与T5X训练实现分别标识。本卡不把指令训练或框架名称当成同一原始骨干。
- NVlabs/GatedDeltaNet官方FAQ说只提供实现、不发布该论文预训练权重，公开dataloader也不是论文FineWeb-Edu语料的无差别替代。未在本地运行其代码验证。

## 公开但未展开的延伸

当前 [state-spaces/mamba官方README](https://github.com/state-spaces/mamba/blob/main/README.md) 还列出 [Mamba-3（2603.15569）](https://arxiv.org/abs/2603.15569)。本轮只核实该入口，未阅读其论文机制，不据此写新结构细节。因此九张卡是为辨清信息流选取的谱系，不能称为截至2026已穷尽全部替代模型。

论文指标、原理表达性与问题理解是不同层次。某个架构支持长状态或高吞吐，不能直接证明它已经学会问题含义；一个有限预算实验失败，也不能替整个架构家族作不可能性证明。
