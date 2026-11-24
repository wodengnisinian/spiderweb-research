# 闭源披露与多模态架构阅读说明

本组收集8条有明确版本范围的代表资料，全部用于架构调查。没有运行、训练或下载模型权重；没有修改前面实验。它不是当前全部模型清单，也不把历史报告自动当作2026年产品内部结构。

OpenAI部分已读 `C:/Users/xxs/.codex/skills/.system/openai-docs/SKILL.md`，本地指定文档区域没有发现可用技术报告。先检索并实际打开OpenAI官方API GPT-4页，因该页不足以建立内部配置，再读用户任务所需的官方OpenAI研究报告与CLIP论文。OpenAI部分的网页来源只用OpenAI官方域名，不采用泄露专家数或第三方架构传闻。

## 已证实的几个分界

- **GPT-4：** 官方2023报告只确认Transformer-style及next-token训练，并明确保留进一步架构细节。不填参数、层数或MoE数量。[报告](https://cdn.openai.com/papers/gpt-4.pdf)
- **GPT-4o：** 2024系统卡确认端到端统一多模态网络，但“统一”不等于没有模态子模块，也不等于公开了全部注意力拓扑。[系统卡](https://cdn.openai.com/gpt-4o-system-card.pdf)
- **Claude 3：** 本次可读官方材料确认模态与训练方法，不能据此重建完整架构；核心PDF完整打开因28.8MB体积限制失败，已保留读取限制，不以未读全文断言某架构不存在。[公告](https://www.anthropic.com/news/claude-3-family)
- **Gemini：** 1.5 Pro为sparse MoE、1.5 Flash为dense；2.5报告将2.5模型称为sparse MoE。不得把Flash一词自动映射为dense，也不得把所有代际都填同一结构。[1.5报告](https://storage.googleapis.com/deepmind-media/gemini/gemini_v1_5_report.pdf)，[2.5报告](https://storage.googleapis.com/deepmind-media/gemini/gemini_v2_5_report.pdf)

## 三层容易混在一起的信息

网络架构描述张量经过哪些模块，例如注意力、MLP、专家路由、视觉编码器、U-Net和VAE。训练目标或阶段描述参数怎么学，例如next-token、对比学习、蒸馏、RLHF或Constitutional AI。产品系统描述如何调用工具、切换模型、检索或串接辅助安全系统。这三层有关联，但不能互相代替。

MoE通常是在一个网络内部按token路由到部分专家参数；它不同于应用把整个请求分给几个独立模型。thinking budget或测试时计算量的控制也不能单独证明某种新网络骨干。Flash由Pro蒸馏，不能解释为每次Flash推理都必须调用Pro。

## 图像模型也不是同一种“Transformer理解器”

CLIP是图文双编码器对齐；其视觉分支有ResNet和ViT选项。ViT把图像patch映射为序列，不能因此把CLIP的文字编码器也叫图像patch处理器。原始CLIP的masked文本Transformer在这里输出匹配向量，不自动成为对话生成模型。[CLIP论文](https://cdn.openai.com/papers/Learning_Transferable_Visual_Models_From_Natural_Language_Supervision.pdf)

LDM/SD v1在压缩图像潜空间中用U-Net逐步去噪，并用文字条件cross-attention；原始DiT则用latent-patch Transformer代替U-Net，仍属于迭代扩散生成。原始DiT类别条件模型不应被自动描述成文生图对话模型，DiT-XL/2参数也不能填给所有后续产品。[LDM原文](https://arxiv.org/html/2112.10752v2)，[DiT原文](https://arxiv.org/html/2212.09748v2)

## 阅读与日期边界

每条JSON保留实际读到的章节，不声称通读所有100页级报告。部分CVF PDF访问403或过大，已改读同一原论文的作者arXiv HTML。Gemini官方文件名可能更新，JSON没有把arXiv当前修订号硬套给另一个官方PDF；日期只写能确认的精度。Claude 3完整卡未能打开的事实单独披露，不用上一代模型卡替它补全。

这些资料说明有哪些公开的计算组件，不证明某组件已经理解任意问题；架构名称、模态支持、训练方法和理解能力证据需要分别陈述。
