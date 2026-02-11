---
title: ResearcherZero 架构设计 -- Context
date: 2026-02-01 10:13:27
updated: 2026-02-11 23:07:27
tags: researcher-zero-arch-design
categories: [ResearcherZero]
---
## Introduction
经过多个Agent项目的算法设计实践，我认为一个 Agent 的设计可以用 Context，Memory，Learning，Reasoning 这样的框架去展开思考。
- **Context**: [Context Engineering](https://platform.claude.com/docs/en/build-with-claude/context-windows) 是25年非常热门的一个词，大多数开发者将其认为是一种工程优化思路，但我想从更抽象一层去定义的 Context，它不是工程意义上的输入参数，而是一个 AI 生命体在某一刻“作为某种身份**存在**”的处境。就像一个工人之所以是工人，不仅是因为他脑中存了多少知识，而是因为他此刻站在工地上，手里拿着工具，面前有明确的任务与约束 —— 这构成了他的“当下状态”。
- **Memory**: 让这种处境(Context)可以跨时间延续。人类工人会记得昨天做到哪一步、哪些规则重要，Agent 也需要记忆系统来进行状态的存储，更新，和读取。
- **Learning**: 身份在时间中的成长。Agent 会通过反馈或学习不断调整和更新自己的 Context。
- **Reasoning**: 如何消费 Context。

本篇文章介绍 ResearcherZero 的 Context 设计。

## Context 设计
> ResearcherZero 作为一个研究者，什么语境/状态让他是一个研究者？

ResearcherZero 的目标不是简单回答问题，而是像一个长期协作的研究助手一样，能够在不同任务之间保持一致的理解与积累。这里的 Context 并不是聊天窗口里的历史消息，而是系统内部保存的一组结构化信息，用来支撑后续每一步研究、检索、写作和判断。我把它拆成四类最关键的状态。

### 1. 基本语境：这个研究领域是什么，长什么样
> 当我们进入一个研究方向时，首先需要的是“坐标系”。

ResearcherZero 会尝试建立两类基础框架：
1. <u>基本信息</u>：这个领域的基本介绍
这个领域是什么，有什么背景，基本认知

2. <u>分类框架</u>：这个领域怎么构建
任何研究领域可以由多个 Category + 多个 Concept 编织而成，比如大模型训练可以分成 Arch, Data, Training, Evaluation, Inference 几个 Categories，其中 Data 下面又有比如 Deduplication，High Quality Data Synthesis等 Concept。

### 2. 认知层：进行理解、判断、推理、决策与规划的心理知识
> 不只是收集信息，还要有高层抽象，最新进展，有效方法等认知

ResearcherZero 会维护两类认知状态：
1. <u>核心挑战</u>：一个 benchmark 测的不是“分数”，而是能力
比如：
    - 长上下文一致性
    - 多步推理
    - 工具使用
    - 可控生成
    
    记录 benchmark ↔ 能力 ↔ 挑战 的对应关系，让系统有评估标尺。

2. <u>关系网络</u>：
不同概念之间的递进或逻辑关系：
    - Chain-of-Thought 属于 Prompting
    - Prompting 影响 Reasoning Ability

### 3. 原子知识单元：Research 世界最小的积木
> Research世界的最小知识单元。

ResearcherZero 会维护四类原子单元：
1. <u>方法优化型Paper</u>：每篇论文都可以抽象成：
    - Problem：解决什么问题
    - Method：核心方法是什么
    - Metrics：怎么评估
    - Insights：关键贡献与启发

    这是建立起研究世界的点。

2. <u>Survey型Paper</u>：研究者经过广泛阅读后产生的框架性认知思考

3. <u>Benchmark</u>：研究者对该领域某些问题的建模与评估设计
    
4. <u>Blog/News</u>：更非专业性，或更工程应用性质的事实，知识，认知等

### 4. 价值对齐：研究助手要符合谁的偏好
> 同样的论文，有人关心理论突破，有人关心工程落地。

因此 Context 里还会保存用户偏好，例如:
- 更关注 Research 还是 Engineering
- 更在意 novelty 还是可复现性
- 信息密度偏高还是偏解释性

ResearcherZero 对 Context 消费后形成的输出的风格会随之调整。


## **总结**：Context 是 ResearcherZero 的存在状态。
ResearcherZero 的关键在于：它通过 Context 把研究世界变成结构化的、可积累的状态空间，使它不仅能回答一次问题，还能在时间中持续形成：
- 领域地图
- 知识积木
- 研究谱系
- 用户偏好一致性

成为一个真正会成长的 AI 研究员。