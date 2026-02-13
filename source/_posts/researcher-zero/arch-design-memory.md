---
title: ResearcherZero 架构设计 -- Memory
date: 2026-02-11 23:07:27
updated: 2026-02-13 09:07:27
tags: researcher-zero-arch-design
categories: [ResearcherZero]
---
## Introduction
经过多个Agent项目的算法设计实践，我认为一个 Agent 的设计可以用 Context，Memory，Learning，Reasoning 这样的框架去展开思考。
- **[Context](/2026/02/01/researcher-zero/arch-design-context/)**: 一个 AI 生命体在某一刻“作为某种身份**存在**”的处境。就像一个工人之所以是工人，不仅是因为他脑中存了多少知识，而是因为他此刻站在工地上，手里拿着工具，面前有明确的任务与约束 —— 这构成了他的“当下状态”。
- **[Memory](/2026/02/11/researcher-zero/arch-design-memory/)**: 让这种存在(Context)可以跨时间延续的记忆机制。人类的记忆依赖多个脑区协同工作：海马体负责把短期经历编码并整合为长期记忆，尤其是情景与空间记忆；前额叶皮层参与工作记忆、注意控制与记忆提取策略；杏仁核调节情绪强度，使情绪事件更易被记住；长期记忆的具体内容则分布式存储在新皮层。整体上，记忆不是集中在单一点，而是一个由编码、巩固与再激活构成的网络系统。受到 [A Survey on the Memory Mechanism](https://arxiv.org/pdf/2404.13501) 的启发，我也将 Agent 的 Memory 设计拆成 **存储**、**更新**、**读取** 三个过程，这和前面提到的人类的编码、巩固、再激活也是一一对应的。
- **[Learning](/2026/02/13/researcher-zero/arch-design-learning/)**: 一个 AI 生命体随着时间流逝而产生的成长。Agent 会通过反馈或学习不断调整和更新自己的 Context。
- **Reasoning**: 如何消费 Context。

本篇文章介绍 ResearcherZero 的 Memory 设计。

## Memory 设计
> ResearcherZero 怎么样记录其Context

### GraphMemory 的探索
> 为什么经过实践探索后我放弃了 GraphMemory？

在 ResearcherZero Memory 的早期设计中，我尝试了基于 GraphMemory（基于图数据结构）的方案，但在实际工程落地中，我遇到了三个难以调和的核心痛点：

1. **预定义的僵化与重构的高成本**：图结构强依赖于预先定义的 Schema（如点、边的类型）。然而，Agent 的思考是流动的，当需要调整上下文结构时，往往面临着对 Schema 的重构。这种重构在工程上极其繁琐，且之前依赖预定义规则的信息抽取模块也会随之失效。考虑到随着信息网络规模的增长，维护和更新这张图的心理负担很可能变得越来越重。
2. **非常不直观**：其实我在最开始本能地认为 图 会更直观，但这存在一个巨大的误区：人类之所以觉得图直观，是因为能看到类似“思维导图”的视觉呈现，而非图数据结构本身。当图结构被序列化为文本（如三元组列表或 JSON）展示给我们自己或 Agent 时，它实际上是一堆极其晦涩、难以建立全局认知的字符堆叠。失去了渲染层的图，在可读性上远不如结构化文本。
3. **人机协同的阻滞**：Agent 的记忆不应是一个黑盒，它需要支持 Human in the loop，在 Agent 工作的同时，人类可以参与进去 debug 与微调。在 GraphMemory 的设计下，一旦关系网变得庞大，要求人类直接去修改序列化后的图数据将非常痛苦，即使为此再开发一个可视化界面也是一样。这种对人类不友好的数据形态，切断了人机协作优化 Context 的路径。

### Markdown 文件系统作为 Memory
> 回归本质：像文件系统一样的记忆

**核心思想**：
- <u>每个文件夹是一个研究领域</u>：这样做就和 [Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) 的设计很相似，因为不同的研究领域可以看作是不同的 Context 切换，所以和 Skills 的设计思想相当契合，这也体现了文件系统作为 Memory 的优势。
- <u>每个文件有一定规则的层级</u>：这样做可以通过天然的层级支持渐进式加载，比如在无需全量细节的情况下，只需要加载一定标题层级（如H1，H2），以及可以只抽取每个层级的前k句话，从而能在更少的上下文token消耗下，达到更高的信噪比。

#### Memory的存储
> 既然放弃了图数据库，那么 ResearcherZero 的大脑文件系统长什么样？

我将 Memory 的存储设计为一个多层级的文件系统，其具体设计与 [Context 设计](/researcher-zero/arch-design-context/) 保持高度对齐。

类似于 Claude 的 **Skills** 概念，我将每一个研究领域视为一个独立的文件夹。当 ResearcherZero 切换研究任务时，本质上是在切换不同的领域文件夹，从而加载不同的 Context。

在每个领域文件夹内部，我设计了四个维度的信息分层：

```bash
/Domain
├── Basic_Context (基本语境层)
│   ├── basic_info.md       # 基础定义：该领域是什么
│   └── taxonomy.md         # 分类网络：Category + Concept 的层级树
├── Cognition (认知层)
│   ├── main_challenge.md   # 核心挑战：当前领域未解决的问题
│   └── network.md          # 关系网络：梳理概念间的关联与演化脉络
├── Atomic_Knowledge (原子知识层)[但我在实现的时候应该不会特地划分四个文件夹，而是用 YAML Frontmatter 里的tag区分]
│   ├── methods/            # 具体算法与论文
│   ├── benchmarks/         # 评测指标 (反映当前的挑战)
│   ├── surveys/            # 综述与思想 (专家分类方法/Abstract哲学)
│   └── blogs/              # 较为发散的网络文章
└── Alignment (价值对齐层)
    └── human_preference.md # 人类偏好与负面约束
```

1. <u>基本语境层</u>：这个研究领域是什么，大概长什么样。`basic_info.md` 提供了最基础的定义，而 `taxonomy.md` 则凝练一个分类设计。这确保了 ResearcherZero 即使在没有具体知识时，也能知道自己不知道什么，并能准确地定位知识的坐标。注意，这里 `taxonomy.md` 的层级设计不用再重蹈 GraphMemory 的覆辙，是任意格式的文本都行，只要能清晰表达 Category 和 Concept 即可。
2. <u>认知层</u>：进行理解、判断、推理、决策与规划的心理知识。`main_challenge.md` 记录了该领域的核心难题，`network.md` 则记录了概念之间的流转关系。这一层赋予了 ResearcherZero “研究品味”，使其能判断哪些工作是有价值的，哪些是过时的，也赋予了 ResearcherZero 知识联系的深度。
3. <u>原子知识层</u>：这个研究领域的知识块。通过 YAML Frontmatter 中的 Tag（如 survey, method, benchmark, blog）、Category 和 Concept 进行聚类。
    - 对于 Survey，不仅记录内容，更着重提取其设计哲学，因为这往往代表了该领域的高层认知。
    - 对于 Benchmark，不仅是量化数字，更着重提取其反应的当前领域的挑战。
4. <u>价值对齐层</u>：`human_preference.md` 作为一个独立模块，显式地记录了个人的偏好。

#### Memory的读取
> 如何从当前的 Memory 存储中构建出 ResearcherZero 的 Context？

1. <u>基本语境构造</u>：基础信息(`basic_info.md`) + 分类网络(`taxonomy.md`)
2. <u>认知构造</u>：概念网络(`network.md`) + 核心挑战(`main_challenge.md`) + 高层抽象/哲学(浅层加载各个`survey.md`) 
3. <u>原子知识</u>：原始为空，但提供搜索知识块工具，可按category，concept(`taxonomy.md`有提供)进行目录搜索，渐进式加载

#### Memory的管理(非MVP版本实现)
> 如何更新和遗忘？

- 更新机制：
    1. ResearcherZero 在 **Learning** 过程中更新记忆。
    2. **human in the loop** 介入要求更新某些地方/反馈错误或out of date触发/...
- 遗忘机制：类似突触的机制，触发越多排序越好，触发越少，随时间或topk机制就被遗忘

## Conclusion
ResearcherZero 的 Memory 设计经历了一次从 想象简单实则复杂 到 本质上的实用 的回归。放弃 GraphMemory 而转向 Markdown 文件系统，并非技术的倒退，而是对 **LLM Native** 与 **Human-in-the-loop** 的追求。在这样的设计下，人类可以轻松地介入，理解 Agent，同时具有良好的 Scalability。

至此，Context 与 Memory 的拼图已经严丝合缝。接下来，我会探索这个 AI 生命体如何利用这些记忆去进行 **Learning** 与 **Reasoning**，让内部状态真正转化为智能。