---
title: ResearcherZero 架构设计 -- Context
date: 2026-02-01 10:13:27
tags: researcher-zero-arch-design
categories: [ResearcherZero]
---
## Introduction
我将一个 Agent 的实现简单地分为 Context，Memory，Learning，Reasoning 四大块。
- **Context**: Context 不是工程意义上的输入参数，而是一个智能体在某一刻“作为某种身份**存在**”的处境。就像一个工人之所以是工人，不仅是因为他脑中存了多少知识，而是因为他此刻站在工地上，手里拿着工具，面前有明确的任务与约束 —— 这构成了他的“当下状态”。例如，一个 Agent 被定义为文本核查员，那么它的 Context 除了模型的参数以外，还有它此刻所处的工作场景：这段文本、需要核对的目标、以及当前进度。这些共同构成了它作为“核查员”这一身份的当下处境。
- **Memory**: 让这种处境(Context)可以跨时间延续。人类工人会记得昨天做到哪一步、哪些规则重要，Agent 也需要记忆系统来进行状态的存储，更新，和读取。
- **Learning**: 身份在时间中的成长。Agent 会通过反馈或学习不断调整和更新自己的 Context。
- **Reasoning**: 如何消费 Context。

本篇文章介绍 ResearcherZero 的 Context 设计。

## Context 设计
> ResearcherZero 如何“知道自己在研究什么”

ResearcherZero 的目标不是简单回答问题，而是像一个长期协作的研究助手一样，能够在不同任务之间保持一致的理解与积累。这里的 Context 并不是“聊天窗口里的历史消息”，而是系统内部保存的一组结构化信息，用来支撑后续每一步研究、检索、写作和判断。我把它拆成四类最关键的状态。

### 1. 基本语境：这个领域的地图是什么
> 当我们进入一个研究方向时，首先需要的是“坐标系”。

ResearcherZero 会尝试建立两类基础框架：
1. <u>分类框架</u>：这个领域怎么划分
比如 NLP 可以简单分成：
    - 信息抽取
    - 机器翻译
    - 对话系统
    - ...

    这些分类帮助系统快速知道：当前问题属于哪一块。

2. <u>范式框架</u>：主流方法的基本套路
很多领域并不是靠“具体模型名字”组织，而是靠范式：
    - RNN 时代的序列建模
    - Transformer 的注意力结构
    - Vision-Language 的 Encoder + Projector + LLM 组合

    范式让系统理解：论文创新通常发生在哪个模块，而不是孤立的技巧。

### 2. 原子知识单元：Research 世界最小的积木
> Research世界的最小知识单元。

ResearcherZero 会维护三类原子单元：
1. <u>论文快照</u>：每篇论文都可以抽象成：
    - Problem：解决什么问题
    - Method：核心方法是什么
    - Metrics：怎么评估
    - Insights：关键贡献与启发

    这是建立起研究世界的点。
2. <u>概念网络</u>：很多重要东西不是论文标题，而是概念
    - Chain-of-Thought 属于 Prompting
    - Prompting 影响 Reasoning Ability
    - Reasoning 与 Format Following 有关联
    
    这是研究世界的边，将点链接成一个图谱

### 3. 认知层：什么才算“重要进展”
> 不只是收集信息，还要知道什么算重要进展。

ResearcherZero 会维护两类认知状态：
1. <u>核心挑战</u>：一个 benchmark 测的不是“分数”，而是能力
比如：
    - 长上下文一致性
    - 多步推理
    - 工具使用
    - 可控生成
    
    记录 benchmark ↔ 能力 ↔ 挑战 的对应关系，让系统有评估标尺。

2. <u>SOTA 追踪</u>：现在最好的方法是什么
研究领域的“最强结果”是动态的，而且经常有争议。Context 会维护：
    - benchmark 上当前领先的方法
    - 方法属于哪个范式
    - 改进是否可信（数据集是否变化）
    
    这避免系统停留在过时结论。


### 4. 价值对齐：研究助手要符合谁的偏好
> 同样的论文，有人关心理论突破，有人关心工程落地。

因此 Context 里还会保存用户偏好，例如:
- 更关注 Research 还是 Engineering
- 更在意 novelty 还是可复现性
- 信息密度偏高还是偏解释性

ResearcherZero 对 Context 的消费风格会随之调整。


## **总结**：Context 是 ResearcherZero 的“长期记忆骨架”。
如果说大模型擅长生成语言，那么 ResearcherZero 的关键在于：它通过 Context 把研究世界变成结构化的、可积累的状态空间。这使得它不仅能回答一次问题，还能在时间中持续形成：
- 领域地图
- 知识积木
- 研究谱系
- 用户偏好一致性

最终成为一个真正“会成长”的研究型 AI Employee。