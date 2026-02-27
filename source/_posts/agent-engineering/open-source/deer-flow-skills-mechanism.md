---
title: DeerFlow 的 Skills 实现机制
date: 2026-02-27 21:07:27
updated: 2026-02-27 21:07:27
tags: [agent-engineering, mechanism-interpret]
categories: [Agent Engineering, Mechanism Interpret]
---
# DeerFlow Skills 运作机制（代码级拆解）
最近想自己实现一个支持 Skills 的 Agent 系统，于是阅读了 [DeerFlow](https://github.com/bytedance/deer-flow) 的实现，在此沉淀一篇运作机制说明。

> <u>目标读者</u>：想自己实现一套“可插拔 Skill 机制”的 Agent 系统开发者。  
> <u>结论先行</u>：DeerFlow 的 Skill 机制是“**Skill 元数据注入提示词 + LLM 按需读取 SKILL.md + 沙箱 Terminal 指令调用工具**”的模式。

## 1. 整体架构：Skills 在系统里的位置

Skill 机制由 5 层组成：

1. **Skill 文件层**（`skills/public|custom/*/SKILL.md`）  
2. **加载与状态层**（`backend/src/skills/*` + `extensions_config.json`）  
3. **Prompt 注入层**（`backend/src/agents/lead_agent/prompt.py`）  
4. **执行环境层**（`/mnt/skills` 挂载与 `read_file` 工具可读）  
5. **管理控制层**（Gateway `/api/skills*` + 前端 Settings/Artifacts）

这五层串起来，形成“发现 -> 启用 -> 注入 -> 读取 -> 执行”的完整回路。


## 2. Skill 数据模型与目录约定

### 2.1 数据模型

`backend/src/skills/types.py` 里用 `Skill` dataclass 表示一个技能，核心字段：

- `name`
- `description`
- `license`
- `skill_dir`
- `skill_file`
- `category`（`public` 或 `custom`）
- `enabled`

并提供：

- `get_container_path()` -> `/mnt/skills/{category}/{dir}`
- `get_container_file_path()` -> `/mnt/skills/{category}/{dir}/SKILL.md`

### 2.2 目录结构

默认目录在项目根：

```text
skills/
  public/
    <skill-dir>/SKILL.md
  custom/
    <skill-dir>/SKILL.md
```

其中 `public` 是内置技能，`custom` 是用户安装/自定义技能。

## 3. Skill 发现与解析（Loader）

核心代码：`backend/src/skills/loader.py` + `backend/src/skills/parser.py`

### 3.1 路径解析

`load_skills()` 会优先用 `config.skills.path`（`backend/src/config/skills_config.py`），否则 fallback 到 `get_skills_root_path()`（默认 `deer-flow/skills`）。

### 3.2 扫描逻辑

`load_skills()` 只扫描两层：

- `skills/public/*/SKILL.md`
- `skills/custom/*/SKILL.md`

每个子目录若存在 `SKILL.md`，就调用 `parse_skill_file()` 解析。

### 3.3 Frontmatter 解析逻辑

`parse_skill_file()` 用正则匹配最前面的 YAML frontmatter，然后按“每行 `key: value`”做简化解析，至少要有：

- `name`
- `description`

解析成功返回 `Skill` 对象。

### 3.4 enabled 状态合并

`load_skills()` 之后会读取 `ExtensionsConfig.from_file()`（`backend/src/config/extensions_config.py`），逐个执行：

```python
skill.enabled = extensions_config.is_skill_enabled(skill.name, skill.category)
```

如果 `enabled_only=True`（给 Prompt 注入时就是这个模式），会过滤掉禁用技能。

## 4. Skills 如何进入 Agent 提示词

核心代码：`backend/src/agents/lead_agent/prompt.py`

链路：

1. `make_lead_agent()`（`agent.py`）
2. `apply_prompt_template()`
3. `get_skills_prompt_section()`
4. `load_skills(enabled_only=True)`

`get_skills_prompt_section()` 会拼出：

- `<skill_system>...</skill_system>`
- 里面有 `<available_skills>`
- 每个 skill 含：
  - `name`
  - `description`
  - `location`（绝对容器路径，如 `/mnt/skills/public/data-analysis/SKILL.md`）

同时在提示词中硬编码了 Skill 使用约束（关键）：

1. 用户请求匹配 skill use case 时，先 `read_file` 读 skill 主文件  
2. 按需增量读取 skill 引用资源（scripts/references/assets）  
3. 严格按 skill 指令执行

这意味着 DeerFlow 的 Skill 触发是 **LLM 决策驱动**，不是规则引擎自动触发。

## 5. 为什么 Agent 能读到 `/mnt/skills/...`

要点：Prompt 给的是容器路径，运行时要保证该路径真实可读。

### 5.1 Local Sandbox 模式

- `backend/src/sandbox/local/local_sandbox_provider.py`
  - 把 `config.skills.get_skills_path()` 映射到 `config.skills.container_path`（默认 `/mnt/skills`）
- `backend/src/sandbox/local/local_sandbox.py`
  - `_resolve_path()` 把 `/mnt/skills/...` 反解为本地真实路径

### 5.2 AIO/Docker Sandbox 模式

- `backend/src/community/aio_sandbox/aio_sandbox_provider.py`
  - `_get_skills_mount()` 返回 `(host_skills_path, /mnt/skills, True)`
  - 以**只读挂载**注入容器

### 5.3 工具调用路径

`read_file` 工具实现于 `backend/src/sandbox/tools.py`，调用 `sandbox.read_file(path)`；因此只要 `/mnt/skills` 映射成功，Agent 就能按 prompt 指示读取 SKILL.md。

## 6. 子代理（task）也会继承 Skills 机制

核心代码：`backend/src/tools/builtins/task_tool.py`

`task_tool()` 在创建子代理前会再次调用 `get_skills_prompt_section()`，并把结果追加到子代理 `system_prompt`：

```python
overrides["system_prompt"] = config.system_prompt + "\n\n" + skills_section
```

所以主代理和子代理都遵守同一套 skill-first 规则。

## 7. 管理控制面：列出 / 开关 / 安装 Skill

### 7.1 列出与开关

后端接口：`backend/src/gateway/routers/skills.py`

- `GET /api/skills`：返回所有技能及 enabled 状态
- `PUT /api/skills/{skill_name}`：写入 `extensions_config.json` 的 `skills` 字段

前端调用：

- `frontend/src/core/skills/api.ts`
- `frontend/src/components/workspace/settings/skill-settings-page.tsx`

### 7.2 安装 `.skill` 包

后端：

- `POST /api/skills/install`
- 从线程 artifacts 虚拟路径解析到真实文件（`resolve_thread_virtual_path`）
- 校验 `.skill` 是 ZIP、校验 `SKILL.md` frontmatter
- 解压后复制到 `skills/custom/{skill_name}`

前端入口：

- artifacts 文件列表/详情中的 “Install” 按钮
- 对应组件：
  - `frontend/src/components/workspace/artifacts/artifact-file-list.tsx`
  - `frontend/src/components/workspace/artifacts/artifact-file-detail.tsx`

### 7.3 `.skill` 文件预览

- `backend/src/gateway/routers/artifacts.py` 支持 `xxx.skill/SKILL.md` 的“压缩包内文件读取”
- `frontend/src/core/artifacts/loader.ts` 读取 `.skill` 时自动补 `/SKILL.md`

## 8. 一次完整请求中的 Skills 时序

```text
用户发起请求
  -> make_lead_agent()
  -> get_skills_prompt_section() 从 enabled skills 生成 <available_skills>
  -> LLM看到技能目录（name/description/location）
  -> LLM判断命中某个技能
  -> 调用 read_file("/mnt/skills/.../SKILL.md")
  -> 按 SKILL.md 指令继续调用 bash/read_file/write_file/... 执行
  -> 产出结果到 /mnt/user-data/outputs 并返回
```

## 9. 对自建系统最有参考价值的设计点

如果要做自己的 Skill 机制，DeerFlow 这套实现可抽象成：

1. **Skill 作为“声明式工作流文档”**，而不是硬编码流程节点  
2. **Prompt 注入只放元数据**（name/description/path），正文按需读取，节省上下文  
3. **运行时路径统一抽象**（容器路径 + 本地映射/挂载），让 Skill 指令跨环境一致  
4. **控制面独立**（启停、安装、列表 API），并持久化到配置文件  
5. **主代理/子代理共用 Skill 语义**，避免行为割裂


## 10. 当前实现里的边界与注意事项（按代码现状）

1. **Skill 触发不是强规则匹配**：依赖模型理解 description 后自行调用 `read_file`。  
2. **enabled 配置键目前按 `skill_name` 存储**（`ExtensionsConfig.is_skill_enabled`），public/custom 同名时无法精确区分。  
3. **`parse_skill_file()` 是简化 frontmatter 解析**，不是完整 YAML 解析器。  
4. **`/api/skills/install` 当前写入路径固定用 `get_skills_root_path()/custom`**，未跟随 `config.skills.path` 自定义路径。  
5. **skills 相关自动化测试目前基本缺失**（`backend/tests` 下无 skill 测试）。


## 11. 关键源码索引（建议按此顺序读）

1. `backend/src/skills/loader.py`
2. `backend/src/skills/parser.py`
3. `backend/src/config/extensions_config.py`
4. `backend/src/agents/lead_agent/prompt.py`
5. `backend/src/tools/builtins/task_tool.py`
6. `backend/src/sandbox/local/local_sandbox_provider.py`
7. `backend/src/community/aio_sandbox/aio_sandbox_provider.py`
8. `backend/src/gateway/routers/skills.py`
9. `frontend/src/core/skills/api.ts`
10. `frontend/src/components/workspace/settings/skill-settings-page.tsx`

