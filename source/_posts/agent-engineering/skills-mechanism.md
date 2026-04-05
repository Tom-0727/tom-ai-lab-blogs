---
title: 互联网中skills的介绍很多，但到底怎么让自己的Agent支持Skills？
date: 2026-02-20 15:07:27
updated: 2026-02-20 15:07:27
tags: [agent-engineering, skills, agent-architecture]
categories: [Agent Engineering]
description: "互联网上关于 Agent Skills 的科普很多，但如何统一实现这套机制却鲜有讨论。本文梳理 Skills 机制的核心设计思路，并分享一个基础实现方案，适合正在开发 Agent 系统的工程师参考。"
---
在开发 [ResearcherZero](/2026/01/29/researcher-zero/intro-researcher-zero/) 的 Learn 特性时，我需要它能支持 [skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) 的机制，但是发现其实虽然很多科普贴，但很少去统一这个机制怎么实现的，所以有此探索。

后续我会分享出我的梳理，以及一个基础的实现。