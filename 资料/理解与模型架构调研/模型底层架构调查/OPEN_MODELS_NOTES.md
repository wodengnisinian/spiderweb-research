# 十个开放权重版本的底层架构核查

资料日期：2026-11-05。只查公开资料，没有下载权重、运行推理、训练模型或修改现有实验。下表针对具体版本，不将同名系列各代视为相同架构。日期是所列官方发布/模型卡日期，不自动等于最早权重上传日。完整逐条来源、阅读范围和缺口在 `open_models.json`。

| 精确版本 | 语言骨干与参数化 | 序列信息怎样混合 | 位置、归一化与FFN | 直接核到的关键数值 |
|---|---|---|---|---|
| Llama3.1-8B-Instruct，2024-07-23 | 稠密decoder-only Transformer | GQA | scaled RoPE；pre-RMSNorm；SwiGLU | Meta配置：32层，4096宽，Q32/KV8 |
| Llama4-Scout-17B-16E-Instruct，2025-04-05 | 自回归MoE骨干，视觉early fusion | iRoPE交错RoPE/noPE注意力；参考实现支持KV头共享 | RMSNorm；参考MoE为SwiGLU专家+共享路径 | 官方卡109B总量、17B激活、16 experts；Scout层数/头数本次未核定 |
| Qwen3-8B，2025-04-29 | 稠密causal Transformer | GQA+QK-Norm | RoPE；pre-RMSNorm；SwiGLU | 36层，4096宽，Q32/KV8；模型卡8.2B |
| Qwen3-Next-80B-A3B-Instruct，2025-09-11 | 混合线性/全注意力骨干+MoE | 3层Gated DeltaNet配1层Gated Attention | 全注意力partial RoPE；zero-centered norm/gated RMSNorm；SiLU门控专家 | 48层，2048宽；512路由专家top10+1共享；80B总/3B激活 |
| DeepSeek-V3原版，2024-12-26 | 因果Transformer，前3层dense FFN、随后MoE | MLA低秩KV潜变量压缩 | decoupled RoPE/YaRN；RMSNorm；SwiGLU专家 | 61层，7168宽；256路由top8+1共享；671B总/37B激活 |
| DeepSeek-R1原版，2025-01-20 | 继承V3-Base骨干 | 同类MLA | 同类RoPE/RMSNorm/MoE；主要区别是后训练 | config仍为DeepseekV3ForCausalLM；61层、7168宽、256/8+1 |
| Mistral-7B-v0.1，2023-09-27 | 稠密decoder-only | GQA+4096滑窗SWA | RoPE；RMSNorm；SiLU门控MLP | 32层，4096宽，Q32/KV8；官方7.3B |
| Mixtral-8x7B-v0.1，2023-12-11技术公告 | decoder-only，稀疏MoE FFN | GQA；所读config滑窗为null | RoPE；RMSNorm；每层8个SiLU门控专家top2 | 32层、4096宽、Q32/KV8；46.7B总/12.9B激活 |
| Gemma3-4B-IT，2025-03-12 | 稠密decoder-only+SigLIP视觉编码器 | GQA，局部/全局层5:1交错 | RoPE；前/后RMSNorm+QK-Norm；GELU门控MLP | Google参考4B配置：34层，2560宽，Q8/KV4，局部窗1024 |
| Phi4原始14B，2024-12-12 | 稠密decoder-only | 全局因果GQA | RoPE；RMSNorm；SiLU门控MLP | 40层，5120宽，Q40/KV10；config使用Phi3ForCausalLM |

## 架构差别应怎样读

**MoE与注意力是两个不同轴。**Mixtral保留GQA，主要把FFN专家化；DeepSeek-V3同时采用MLA与MoE；Qwen3-Next则把线性注意力、门控全注意力和高稀疏MoE组合。专家数描述前馈路由，不能直接拿来解释KV缓存或注意力连接范围。[Mixtral官方公告](https://mistral.ai/news/mixtral-of-experts/)、[DeepSeek-V3报告](https://arxiv.org/html/2412.19437v2)、[Qwen3-Next官方卡](https://huggingface.co/Qwen/Qwen3-Next-80B-A3B-Instruct)。

**R1的推理训练不意味着换了一套骨干。**原始R1由V3-Base通过cold-start、SFT和RL等阶段得到，其配置仍声明DeepseekV3ForCausalLM。R1-Zero的流程、R1原版流程，以及Distill-Qwen/Distill-Llama学生骨干须分开看。[R1原始报告](https://arxiv.org/html/2501.12948v1)、[R1官方配置](https://huggingface.co/deepseek-ai/DeepSeek-R1/blob/56d4cbbb4d29f4355bab4b9a39ccb717a14ad5ad/config.json)。

**同一系列名不保证相同结构。**Qwen3-8B是dense GQA，而Qwen3-Next含Gated DeltaNet与MoE；Gemma3-4B有视觉编码器，1B则没有；Mistral7B-v0.1的4096滑窗不能套给所读Mixtral配置；Phi4的类名沿用Phi3也不意味着权重就是Phi3。[Qwen3报告](https://arxiv.org/html/2505.09388v1)、[Gemma3报告](https://arxiv.org/html/2503.19786v1)、[Mistral配置](https://huggingface.co/mistralai/Mistral-7B-v0.1/blob/main/config.json)、[Mixtral配置](https://huggingface.co/mistralai/Mixtral-8x7B-v0.1/blob/main/config.json)、[Phi4配置](https://huggingface.co/microsoft/phi-4/blob/main/config.json)。

## 必须保留的核查缺口与口径

- Meta的3.1和Scout、Google Gemma3的HF配置在本次工具读取中不可访问；没有绕过访问条件。3.1与Gemma3维度改从开发者公开参考配置核对；Scout的精确层数、宽度和头数留空。Meta博客中的Maverick 128路由专家、shared expert与dense/MoE交替示例不直接套到Scout。
- Qwen3-Next旧GitHub main现已滚动到后续Qwen版本。架构采用明确的80B-A3B-Instruct卡和配置；旧仓库只用2025-09-11的历史News核日期。模型卡说明这一Instruct版本只支持non-thinking，不与同日Thinking权重混同。
- Qwen3-8B卡列原生32768、YaRN扩展131072，config的max_position_embeddings为40960，报告表写128K。这些是不同设置/口径，不能挑一个数当所有场景的统一上限。
- Gemma3官方参考配置使用cleaned tokenizer，可能与HF打包词表存在差异；因此没有把多个来源的词表计数混成一个精确值。FFN源码明确用GELU门控，不应一概写成所有模型都是SwiGLU。
- Phi4卡中的2024-12-12是模型发布日，不把它说成HF公开权重上传日；Mixtral使用2023-12-11官方技术公告日期，不否认更早的权重传播。
- 不把开发者上下文声明、训练长度、配置最大位置或实际可靠语义范围混为一谈；没有进行本机吞吐、长上下文或数值一致性实测。

本组只覆盖所列版本。开放权重不等于训练数据、训练代码及服务系统全部公开；许可证也不同。资料里的组件属于公开骨干，不能反推当前线上产品的RAG、Agent、工具调用、采样策略、系统提示或未披露的服务后端。
