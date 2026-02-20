---
title: 互联网中skills的介绍很多，但到底怎么让自己的Agent支持Skills？
date: 2026-02-20 15:07:27
updated: 2026-02-20 15:07:27
tags: agent-engineering
categories: [Agent Engineering]
---
在开发 [ResearcherZero](/2026/01/29/researcher-zero/intro-researcher-zero/) 的 Learn 特性时，我需要它能支持 [skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) 的机制，但是发现其实虽然很多科普贴，但很少去统一这个机制怎么实现的，所以有此探索。

后续我会分享出我的梳理，以及一个基础的实现。