---
title: 我是如何用 AI 自动获取技术资讯的
date: 2026-03-16 23:43:00
updated: 2026-03-16 23:43:00
tags: AI, AInformer, 工具推荐
categories: [agent-product]
---

## 痛点

每天都有大量的技术信息从各个平台涌现 — GitHub Trending、Hacker News、Reddit、36Kr、虎嗅...

作为一个技术从业者，我既不想错过重要信息，又没有时间逐一刷完所有平台。刷一遍 GitHub Trending 要半小时，刷一遍 Hacker News 又半小时，一天就这么过去了。

更难受的是，大部分内容其实和自己没关系。打开 GitHub Trending，推荐的都是 Java、Go、C++ 的项目，而我关心的是 AI Agent、LLM 应用。刷十条，有八条不相关。

## 解决方案

**与其被信息淹没，不如让 AI 帮我筛选。**

这就是 AInformer —— 一个 AI 驱动的信息聚合与推送工具。

它的原理很简单：

1. **定时抓取** — 每天早上/中午/晚上自动从各个平台拉取热门内容
2. **AI 筛选** — 用 LLM 按我的偏好过滤，只保留相关内容
3. **推送到手** — 通过飞书/钉钉机器人把筛选后的内容推给我

现在我每天早上花 5 分钟，就能看完昨天最值得关注的技术资讯。

## 核心功能

AInformer 支持多个平台的信息抓取：

| 平台 | 内容类型 |
|------|----------|
| GitHub Trending | AI Agent、工程架构相关的优质仓库 |
| Hacker News | 热门故事和讨论 |
| Reddit | 感兴趣 subreddit 的最新帖子 |
| 36Kr | 科技创业资讯 |
| 虎嗅 | 商业科技资讯 |
| Product Hunt | 新产品发现 |

LLM 会根据我的偏好进行筛选。比如我设置了「关注 AI Agent、LLM 应用、RAG 技术」，那么系统就会自动过滤掉不相关的内容。

## 技术实现

技术栈很轻量：

- **Python 3.13+** — 现代 Python 特性
- **LangGraph** — 构建 Agent 工作流
- **LangChain + OpenAI** — LLM 调用
- **飞书/钉钉 Webhook** — 消息推送

工作流程是这样的：

```
定时触发 → 数据抓取 → LLM 筛选 → 推送通知
```

每天早上 8 点、 中午 12 点、晚上 8 点各跑一次，分时段推送不同类型的内容。

## 快速开始

```bash
# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env
# 填写 OPENAI_API_KEY 和 NOTIFY_WEBHOOK_URLS

# 运行
uv run python main.py

# 按分组执行
uv run python main.py --group morning   # 早间：Hacker News、The Rundown AI
uv run python main.py --group noon      # 中午：36Kr、虎嗅、Reddit
uv run python main.py --group evening   # 晚间：GitHub Trending、Product Hunt
```

也可以配置 cron 定时任务，实现全自动运行。

## 效果

用了两个月下来，有几个明显的感受：

1. **信息质量提高了** — 推送的都是我关心的内容，不再是噪音
2. **时间节省了** — 从每天刷 1 小时变成 5 分钟
3. **知识面更广了** — 以前只刷 GitHub，现在 Reddit、Product Hunt 也会看看

## 展望

后面还想加几个功能：

- **对话式筛选** — 通过飞书机器人对话，进一步细化筛选条件
- **历史记录** — 把筛选过的内容存到知识库，方便回顾
- **推荐算法** — 根据我的阅读反馈，智能调整推荐策略

---

如果你也被信息过载困扰，不妨试试让 AI 帮你筛选。**让信息获取更高效，让 AI 成为你的信息助手。**

项目地址：https://github.com/Tom-0727/AInformer
