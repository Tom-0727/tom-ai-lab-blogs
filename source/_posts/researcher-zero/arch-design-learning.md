---
title: ResearcherZero 架构设计 -- Learning
date: 2026-02-13 09:07:27
updated: 2026-02-13 09:07:27
tags: researcher-zero-arch-design
categories: [ResearcherZero]
---
## Introduction
经过多个Agent项目的算法设计实践，我认为一个 Agent 的设计可以用 Context，Memory，Learning，Reasoning 这样的框架去展开思考。
- **[Context](/2026/02/01/researcher-zero/arch-design-context/)**: 一个 AI 生命体在某一刻“作为某种身份**存在**”的处境。就像一个工人之所以是工人，不仅是因为他脑中存了多少知识，而是因为他此刻站在工地上，手里拿着工具，面前有明确的任务与约束 —— 这构成了他的“当下状态”。
- **[Memory](/2026/02/11/researcher-zero/arch-design-memory/)**: 让这种存在(Context)可以跨时间延续的记忆机制。我将 Agent 的 Memory 设计拆成 **存储**、**更新**、**读取** 三个过程，这和人类记忆的编码、巩固、再激活是一一对应的。
- **[Learning](/2026/02/13/researcher-zero/arch-design-learning/)**: 一个 AI 生命体随着时间流逝而产生的成长。在 Agent 研究领域有一个方向叫 [Self-Evolving](https://arxiv.org/abs/2507.21046)，我认为 Learning 约等于 Self-Evolving，并多一丝「主动」的味道。我的理解是 Agent 自进化(学习)的优化对象有三个，一个是模型参数，一个是运作方式(自己的Code)，还有一个就是 Context。现主流自进化手段是通过 “执行 -> 观察 -> 反思 -> 优化” 的闭环来实现自我提升，它们通常由优化目标函数驱动。而在这里的 Learning 本质是一样的，AI 生命体会通过反馈或学习不断**调整和更新**自己的 Context。
- **Reasoning**: 如何消费 Context。

本篇文章介绍 ResearcherZero 的 Learning 设计。

## ResearcherZero 的 Learning 设计
基于 ResearcherZero 的[愿景](/2026/01/29/researcher-zero/intro-researcher-zero/)，实际上他的 Learning 的设计要解决的就是学什么，怎么学的问题。比如我的 Research 的习惯就是先看 Survey，建立一定程度的框架性认知之后，再看 Benchmark，并通过引用或者道听途说的频次来判断哪些 Benchmark 有影响力，然后精读 Benchmark 来理解这个领域的痛点难点，之后则会通过 Benchmark 去找到 SOTA 的范式或方法，从而掌握这个领域目标或难点的有效解法，最后增量学习时，我会精读 Abstract，如果匹配或感兴趣，就粗读 Experiment，如果指标不行则根据兴趣程度选择继续看看方法还是直接弃掉，如果指标SOTA，则精读。那么 ResearcherZero 最直觉的设计方案就是根据我的习惯去做。

但是我意识到这里存在一个 **[抽象之梯](https://tombarrett.medium.com/up-and-down-the-ladder-of-abstraction-cb73533be751)** 的问题，抽象之梯出自 [S.I.Hayakawa](https://en.wikipedia.org/wiki/S._I._Hayakawa) 的 *Language in Thought and Action*，它的原意是用来讲述思考与表达的艺术，但曾有个朋友和我分享过另一个解读，就是人和人之间的沟通要达到共识是有个抽象之梯存在的，就和小时候父母要你多穿衣服，但是你其实根本不觉得冷，或者没有经受过严重感冒的折磨，所以你无法和父母达成共识。如果 ResearcherZero 直接一个劲猛学，学完用它凝练后的知识体系和你交流，你是无法理解的。当然，我们可以通过chat去对齐，但这个过程通常不会好过，因为会直接面对大量信息，注意，<u>这些很可能是你不知道好坏的信息</u>。另一个类似例子就是开发者用 Claude Code 直接一次生成完整的代码库，在最开始开发者可能会觉得开心，因为 AI Coding 在30分钟完成了他的任务，并且跑通了。但是到后续增量开发的时候，开发者效率越来越慢，越来越痛苦，因为他根本不知道一些代码逻辑在哪里，就会依赖通过 Chat 去调整，但当下的 Coding Agent 能力仍有局限，有些非常细小的改动，它可能需要梳理5分钟才能找到并修改，一修改可能导致另一个位置逻辑又没对上。

另外，Research 是一个长程任务，如果一开始就把路径锁定，将会有数不尽的边缘情况找上门，比如有些领域没有 Survey，有些领域很特殊，和常规的学习路径不一样，原来定义的学习路径就会失效。长程任务下，想让 Agent 完美遵循难，调优更难。

基于上述的现实情况，我会在这里选择克制全自动，转向更多的 Human in the loop，也就是说 ResearcherZero 的学习过程将高度和人类合作。具体来说，我的**设计理念**就是：人类来提出学习路径的指导（输入学习任务），Agent针对学习任务进行学习，在学习的过程中更新自己的 Context。

### ResearcherZero 对具体学习任务的学习机制
> 当人类提出一个具体的学习任务后，ResearcherZero如何进行学习？

#### 运转机制
整体来讲，ResearcherZero的进行学习时的运转设计是：Human in the loop + Plan&Execute + React
- **Human in the loop**：人类下达阶段性学习任务
- **Plan&Execute**：ResearcherZero接收到学习任务，进行拆解，变成更独立，具体，简单的小任务，比如输入是“接下来请学习 Agent Memory 的 Benchmarks”，它可能拆解成 [1. 搜索 Agent Memory Benchmark，并找到最相关的5篇论文；2. 根据搜索结果继续安排学习计划]。然后直接进行 Execute，按照解析后的 Plan 顺序执行。
- **React**：上一步Execute进入第一个Step，然后进行React式地执行，经过多轮搜索后找齐了5篇论文，这时候会发现第二步是需要第一步信息的，怎么办？这时候就要他具有规划能力，它根据情况将计划改写成 [1. ..., 2. 阅读xxx，3. 阅读yyy, ...]，然后继续下一个Step的React。
    - 这里我做了一个比较有意思的设计，就是每个React得到结束标志时，会触发一次总结，然后将这个React的对话全部压缩成一个message，形成一种上下文动态压缩的机制

通过过程的详述，也会发现 Plan&Execute + React 的形式有几个巨大的优势：
1. <u>指令更遵循</u>：因为开头的 Plan，React 过程不断累积上下文导致的指令遵循下降问题得到缓解；
2. <u>路径更可控</u>：相比那种仅将 Plan 作为一种语义指导加入 Context 的做法，直接 Execute 的话，朴素 React 执行路径不可控性得到缓解；
3. <u>处理更灵活</u>：在 Execute 的 Step 级别过程中 React，并配备规划能力，相比朴素 Plan&Execute 又能更灵活应对更多情况。要注意，增加规划能力并不是倒退回 React，因为大部分场景都是简单的，直接用首跳 Plan 可以做完大部分情况下的任务；
4. <u>上下文更好管理</u>：因为 Plan&Execute+React，将过程信息天然以Step级别划分，从而天然适合进行上下文压缩，整个运行过程的每个Step都能在一个相对舒适的上下文长度下进行，相比那种滑动窗口（前面的Step在舒适的上下文空间，后面的Step实则在逐渐窒息的上下文空间）

#### 原子能力设计
根据上述的运转机制，一个最小可行的 AI Researcher 需要以下三种原子能力：
- **规划能力**：制定计划，修改计划的能力
    - *实现设计*：靠规则化输出解析
- **搜索能力**：搜索学习资料的能力
    - *实现设计*：1. 学术搜索（调研后确定用[Semantic Scholar API](https://www.semanticscholar.org/product/api)，极少数的支持语义搜索论文的API）；2. 通用搜索（调研后确定用[Tavily](https://app.tavily.com)，结合Google，Bing等搜索源，稳定，每个月有1000免费积分）
- **读写能力**：读写文件系统的能力
    - *实现设计*：定义：在一个工作区间内，能读取文件，生成文件，并编辑文件的能力。在调研了 [OpenHands](https://github.com/OpenHands/OpenHands)，[OpenInterpreter](https://github.com/openinterpreter/open-interpreter)，[Aider](https://github.com/Aider-AI/aider) 三个工作后，我决定从 Aider 抽取小工具包出来（其实都行）。简单来讲，Aider的关键不在于给模型文件读写权限，而在于把模型从执行者降级为“变更意图生成器”：模型只产出结构化编辑描述（如 SEARCH/REPLACE、unified diff、patch actions），真正的读写由本地引擎负责。这个引擎是分层设计的：P0 先解决文件系统确定性（编辑，异常处理，重试与路径边界）；P1 在局部编辑阶段引入渐进式匹配与容错（精确匹配优先->缩进/上下文差异回退->多策略搜索替换），提高模型输出在真实文件内容漂移情况下的应用成功率；P2 则把修改提升为可验证的动作语义，通过上下文定位与冲突检测实现更强的一致性和可审计性。但是我这里就只达到部分P1能力的文件系统操作能力即可。

## Conclusion
总的来说，ResearcherZero 的 Learning 模块并没有追求那种听起来很酷的“全自动进化”，而是选择了一条更务实的路线：通过 Human-in-the-loop 配合 Plan&Execute + React 的架构，让 Agent 的学习过程变得可控、可调试。这种设计不仅避免了长程任务中常见的「跑偏」问题，更关键的是解决了“抽象之梯”带来的认知断层 —— 确保 Agent 学进脑子里的东西（Context 的更新），是人类真正需要且能理解的。

Learning 篇结束后，就是可以充满想象力地去思考如何消费学到的知识了。
