---
title: "OpenClaw 不是终点 -- Long-Run Agent Harness 和 Agent Team 更可能是未来"
date: 2026-04-08 12:00:00
updated: 2026-04-08 12:00:00
tags: [agent-engineering, agent-architecture, claude-code, human-in-the-loop]
categories: [Agent Engineering]
description: "从深度使用OpenClaw的实践出发，分析其在Context设计、智能底盘和Team协作上的局限，探讨为什么Long-Run Agent Harness和Agent Team才更可能是AI员工系统的未来方向。"
---

## 从兴奋到清醒

最开始接触 OpenClaw 的时候，我和很多人一样兴奋 -- 终于有一个平台能让你把 Agent 部署起来，7x24 小时跑着，感觉"一人公司"真的有可能了。

我甚至专门写了一篇[用 OpenClaw + 飞书打造 AI-Native 博客运营系统](/2026/03/15/agent-product/openclaw-feishu-blog-automation/)，把它接进了自己的工作流。那个阶段，我觉得 OpenClaw 就是 Agent 基础设施的正确方向。

但深度使用了一段时间后，我的看法变了。

不是说 OpenClaw 不好 -- 作为一个 Agent 托管平台，它的产品完成度很高，heartbeat 机制、文件系统约定、多 Agent 部署，这些设计都给了我很大的启发。但我逐渐意识到，**它离真正的"AI 员工"还有本质距离**。这个距离不是功能缺失的问题，而是设计范式的问题。

## OpenClaw 的三个核心局限

### 1. Context Design 导向的是助手，不是自主 Agent

OpenClaw 的 Context 设计 -- 也就是 `USER.md`、`SOUL.md` 这套 bootstrap 文件系统 -- 本质上构建的是一个"你问我答"的交互模式。

这套设计我把它定义为 Context Design。它告诉 Agent：你是谁、你的用户是谁、你应该怎么回应。但问题在于，**这套设计里没有包含一个完备的自进化心智模型**。

什么意思？一个真正能长期工作的 Agent，至少需要具备自我评估的能力 -- 知道自己做得好不好，哪里可以改进。但 OpenClaw 的 Context 里没有这样的机制。没有 evaluator，Agent 就会非常自然地倾向于"做完就行"。

这不是我一个人的观察。Anthropic 自己在 [Harness Design for Long-Running Apps](https://www.anthropic.com/engineering/harness-design-long-running-apps) 这篇博客里就提到了一个关键问题：

> Agents consistently overpraise their own outputs... 模型会快速完成一个 60 分的工作并倾向于满足。

Anthropic 的解决方案是引入独立的 Evaluator 角色 -- 把"生成"和"评估"分开，用结构化的评分标准和主动测试来对抗这种自满倾向。这和 GAN 的思路很像：Generator 和 Discriminator 分离，才能持续提升质量。

而 OpenClaw 目前的架构里，这一层是缺失的。

### 2. 智能底盘没有突破

坦率地说，OpenClaw 的 Agent 智能水平和直接用 Claude Code 相比，并没有本质提升。它的底层还是一个 naive React loop -- 接收指令、执行工具调用、返回结果。

我觉得一个 Agent 框架的价值，不应该只是提供一个部署壳。**它应该让 Agent 变得更聪明** -- 通过更好的上下文管理、更智能的任务分解、更有效的经验积累，让同一个基座模型在框架的加持下做出更好的决策。

但目前的 OpenClaw 更多是在"托管"层面解决问题，而不是在"智能"层面。

### 3. 不能有效支持 Team 概念

我尝试过把多个通过 OpenClaw 部署的 Agents 放在一个群聊里，让它们能看到彼此的信息。结果发现，**它们并没有任何有效机制来遵循自己的身份并朝着同一个目标前进**。

每个 Agent 都在各说各话。没有身份边界的约束，没有任务分配的协议，没有协调冲突的机制。把 Agent 放在一起不等于 Team -- 就像把五个人扔进一个房间，不给他们分工和流程，他们不会自动变成一个团队。

## 为什么 Long-Run Agent Harness 更可能是方向

经过这些实践，我做了一个决定：**不在 OpenClaw 上继续改了，直接自己造一个 Agent Harness。**

原因很简单。作为一个算法工程师，加上现在 coding agent 的能力，在别人的框架上做二次开发的效率，已经远不如直接按自己的需求从头搭建。

### Heartbeat 的启发

OpenClaw 给我最大的启发是 heartbeat 机制。已知 Codex 和 Claude Code 都有自己的 SDK 可以使用，那要让 Agent 长期运行，最简单的方式就是给它加一个 heartbeat -- 定期唤醒、检查状态、继续工作。

我基于这个思路做了 [Long-Run Agent Harness](https://github.com/Tom-0727/long-run-agent-harness)。但 heartbeat 只是起点，**更深的问题是：怎么让 Agent 持续做好一件事，并且持续优化？**

### 从"能跑"到"能成长"

这是我在 harness 设计中花了最多时间思考的部分。核心设计包括几个关键点：

**Knowledge 和 Episodes 分层。** 把 Agent 的记忆分成两层：Episodes 是有边界的执行记录（一次任务尝试的完整过程），Knowledge 是从多次 episode 中提炼出来的可复用洞察。这个区分非常关键 -- 不是所有经历都值得记住，只有反复出现的模式才值得沉淀。

**Evaluator 机制。** 受 Anthropic 那篇博客的启发，我在 harness 里设计了自我评估的环节。Agent 每完成若干个 episode，就触发一次 evaluation -- 检查工作是否偏离目标，哪些能力可以沉淀成 skill，哪些知识需要更新或删除。

**学习图谱：task → episode → reflection → knowledge / skill。** 这是整个自进化机制的核心路径。Agent 不是在盲目积累信息，而是沿着一条有方向的路径把经验转化为能力。

和 Anthropic 提出的三层架构（Planner / Generator / Evaluator）相比，我的设计更强调**时间维度上的积累** -- 不只是在单次任务内分角色协作，而是让 Agent 跨任务、跨时间地成长。Anthropic 的方案解决的是"单次任务怎么做好"，我想解决的是"怎么让 Agent 越做越好"。

### Human in the Loop 的位置

另一个我觉得很重要的设计选择是 Human in the Loop。在 harness 里，人类不是 Agent 的"用户"，而是它的"协作者" -- 通过 mailbox 机制异步通信，在关键决策点介入，在高风险操作前确认。

这不是对 Agent 能力的不信任，而是一种务实的判断：**现阶段的 Agent 在执行层面已经很强了，但在判断层面还需要人类的校准**。与其让 Agent 独自走偏然后花更多时间纠正，不如在关键节点让人类看一眼。

## Agent Team：方向确定，路径还在探索

关于 Agent Team，坦率地说，我目前还没有想清楚很多事情。

从 OpenClaw 的实践中我观察到的核心问题是：多个 Agent 同时存在时，缺少有效的协调机制。可能的方向包括明确的身份边界定义、结构化的任务分配协议、共享但有权限控制的 Context -- 但这些目前都还是猜想，没有经过充分验证。

我目前把精力集中在 Long-Run 这条线上，先解决"一个 Agent 怎么长期做好一件事"的问题。Team 是下一步，但前提是每个个体先足够强。

## 写在最后

OpenClaw 是一个很好的起点。它让更多人看到了 Agent 长期运行的可能性，它的 heartbeat 机制和文件系统约定启发了很多后来的设计 -- 包括我自己的。

但从"助手"到"AI 生命体"之间，还有 Context 设计、自进化机制、Team 协作这三座大山要翻。

先让 Agent 能长期运行并持续变强，再考虑让它们学会协作。这是我当下的判断，也是 [Long-Run Agent Harness](https://github.com/Tom-0727/long-run-agent-harness) 正在做的事情。

如果你也在思考怎么让 Agent 不只是"能用"，而是真正成为长期共事的伙伴，欢迎交流。
