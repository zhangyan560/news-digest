# AI 与开源技术日报 · 2026-10-26

> 生成于 2026-10-26 20:06（北京时间）· 时间窗口：最近 48 小时 · 采集 117 条 → 去重后 76 条 → 入选 20 条
> 搜索：HN Algolia（免密钥） · 抓取：本地抓取（requests + trafilatura） · 摘要：抽取式 TextRank（免密钥）（摘要为原文摘录，英文来源保留英文）

## 今日概览

- **大模型与 AI 应用**：OpenAI and Anthropic cut their LLM prices by up to 80% within a few months. Why?
- **开源项目与版本发布**：R/open source bans all solo projects and projects using LLMs
- **AI 研究论文**：Tradeoff-Aware Territory Design: A Multi-Objective Decision System for Enterprise Customer-to-Seller Allocation
- **开发者工具与基础设施**：PaperPilot – Zero-Cloud, Pure-Rust PDF Engine with WASM and MCP

## 大模型与 AI 应用（6）

### 1. [OpenAI and Anthropic cut their LLM prices by up to 80% within a few months. Why?](https://minimaxir.com/2026/10/cheap-llms/)
<sub>HN 搜索 · 10-26 05:11 · HN 346 分 · 同见：Hacker News 首页</sub>

Let’s look at a quick timeline of the major LLM model announcements from both OpenAI and Anthropic over the past few months. The theory is that OpenAI and Anthropic are loss-leading just like what Uber and Lyft did to the ridesharing industry in the 2010s, but unlike then, OpenAI and Anthropic are not a duopoly who…

`Anthropic` `OpenAI` `Opus` `Sol`

### 2. [Making My Blog Readable by AI Agents](https://deallocatedobjects.com/posts/making-my-blog-readable-by-ai-agents)
<sub>HN 搜索 · 10-25 05:21 · HN 36 分</sub>

And the .md responses send a Link: <...>; rel="canonical" header pointing at the HTML page, plus X-Robots-Tag: noindex, so Google doesn’t treat them as duplicate copies of every post. llms.txt# /llms.txt is a plain markdown file at the root of the site that tells an agent what it’s looking at. Mine has a one-line…

`URL` `markdown` `HTML` `post`

### 3. [30 个 Agent 背后：花椒如何建设可持续演进的企业 AI 能力？](https://www.infoq.cn/article/O7lcxqKD2avRPbNoMmtg?utm_source=rss&utm_medium=article)
<sub>InfoQ 中文 · 10-26 20:06</sub>

今年最大的一个变化是，企业做 Agent 的门槛越来越低，但做出一个能完成任务的 Agent，与让它在业务中持续稳定运行，还存在一定的距离。 花椒 Agent 平台背后的技术思考 业务与技术的边界，是花椒设计 Agent 平台时重点考虑的问题，随着 Agent 应用越来越多，花椒发现，平台本身也需要做减法。

`Agent` `AI` `花椒` `平台`

### 4. [模型好选，搜索难做：一个投研Agent的两年开发历程](https://www.infoq.cn/article/NrUkJExfuuFOICsjVYbb?utm_source=rss&utm_medium=article)
<sub>InfoQ 中文 · 10-26 20:06</sub>

腾讯云的联网搜索 API 于 2025 年上线，主力接口叫 SearchPro。 他的 Agent 向 SearchPro 发出请求时，除了问题，还会根据任务设置检索范围和时间条件。

`搜索` `陈万` `Agent` `元宝`

### 5. [从 Agent 工程化到任务交付，解读 AI 走向生产的关键挑战｜QCon 上海 2026 圆满收官](https://www.infoq.cn/article/0C1Wgt7N9NzM6KjHSFeA?utm_source=rss&utm_medium=article)
<sub>InfoQ 中文 · 10-26 19:53</sub>

从 Agent 到自主智能 上午第一场演讲中，极客邦科技总编赵钰莹以《从 Agent 到自主智能：2026 AI 技术演进与 2027 趋势前瞻》为题，回顾了 AI 从模型能力竞争走向 Agent 工程化的过程。 Agentic Infra：让基础设施支撑 Agent，也让 Agent 改造基础设施…

`AI` `Agent` `企业` `落地`

### 6. [Kimi K3.1 Pro 发布：代码超 GPT-6 Astra、开放权重版主动移除网络攻防能力](https://www.oschina.net/news/503221)
<sub>开源中国 · 10-26 19:44</sub>

官方给它的定位是"迄今能力最强的模型"，代码、3D 创作、金融研究和长程 Agent 能力提得最狠，还同步出了个 K3.1 Pro Highspeed——同样智能，输出速度约 2~3 倍，价格 2 倍。 Terminal-Bench 4.0 上它得 65...

`开源项目与版本发布` `K3.1` `Pro` `Kimi` `代码`

## 开源项目与版本发布（6）

### 1. [R/open source bans all solo projects and projects using LLMs](https://www.reddit.com/r/opensource/comments/1xelcuf/your_tokens_arent_valuable_no_more_ai)
<sub>HN 搜索 · 10-25 22:05 · HN 88 分</sub>

R/open source bans all solo projects and projects using LLMs

`LLMs` `projects` `open` `source`

### 2. [Show HN: Hurston-1 open source TTS that speak Southern American and Afro-English](https://huggingface.co/destined/hurston-1)
<sub>HN 搜索 · 10-25 09:30 · HN 61 分</sub>

It learned in part from real phone calls between our contributors and AI voice agents, and its phone mode delivers what a caller actually hears: 8 kHz G.711 audio, ready for Twilio and other telephony systems. Testers heard the same sentence from base Maya1 and Hurston-1 in random order, without knowing which was…

`American` `Southern` `English` `Hurston-1`

### 3. [Terraform Google Cloud 8.0 发布：告别“永久 Diff”，代价是破坏性升级](https://www.infoq.cn/article/qJB2DapLThovtxzyOtKW?utm_source=rss&utm_medium=article)
<sub>InfoQ 中文 · 10-26 20:06</sub>

HashiCorp 宣布，Terraform Google Cloud Provider 8.0 现已正式可用。 该 Provider 由 Google Cloud 工程团队、HashiCorp 和 Terraform 社区共同开发，8.0 版本现已在 Terraform Registry 中提供。

`开发者工具与基础设施` `google` `Provider` `资源` `版本`

### 4. [开源中国「AI新生派」走进山东大学软件学院：从技术认知到动手实战，探索 AI 时代开发者成长路径](https://www.oschina.net/news/503219)
<sub>开源中国 · 10-26 17:23</sub>

本次活动由开源中国联合学新社主办，Gitee、模力方舟、openKylin 共建，采用“上午主题分享 + 下午实操演练”的形式，围绕开源基础知识、AI 应用开发、智能硬件、模型适配及开源操作系统等方向展开，帮助高校学生了解前沿技术发展，并通过实践进一步认识 AI 技术与...

`AI` `开源` `山东大学` `新生`

### 5. [CircleCI 正式发布 Machine Runner Orchestrator](https://www.infoq.cn/article/y7YQmP1p42Uj69H1C6uf?utm_source=rss&utm_medium=article)
<sub>InfoQ 中文 · 10-26 17:00</sub>

CircleCI 正式发布 Machine Runner Orchestrator 1.0.0。 GitHub ARC 主要将临时运行器环境作为 Kubernetes 管理的工作负载来创建，而 CircleCI 的 Machine Runner Orchestrator 则专门针对机器运行器的虚拟机。

`Kubernetes` `CircleCI` `CI` `运行`

### 6. [JimuReport v2.5.5 发布，填报增强与 Word 导出专项修复](https://www.oschina.net/news/503217)
<sub>开源中国 · 10-26 13:49</sub>

项目介绍 真正的 AI 报表来了，一句话描述需求，AI 自动生成报表与数据大屏，支持对话式修改报表；同时提供类 Excel 拖拽设计器，兼容 30 余种数据源，轻松应对各类复杂报表场景 :sparkles: 积木报表是一款免费的数据可视化报表工具，集报表、打印、大屏、仪表盘于一体，像搭积木一样完全在线设计。…

`报表` `AI` `大屏` `数据源`

## AI 研究论文（6）

### 1. [Tradeoff-Aware Territory Design: A Multi-Objective Decision System for Enterprise Customer-to-Seller Allocation](https://arxiv.org/abs/2610.31701)
<sub>arXiv cs.AI · 10-26 12:00</sub>

Historical backtesting shows that optimizer-generated scenarios substantially improve assignment compliance while maintaining comparable seller-level opportunity distribution. In production planning, adopted scenarios improved both assignment compliance and opportunity balance relative to the previous baseline.

`Enterprise` `GTM` `opportunity` `Tradeoff-Aware`

### 2. [Patronizing and Condescending Language Detection in English and Mandarin](https://arxiv.org/abs/2610.31808)
<sub>arXiv cs.AI · 10-26 12:00</sub>

Our first approach uses static word embeddings and a convolutional neural network for classification, while our second approach uses pre-trained BERT embeddings fine-tuned for the PCL task. Our second approach was considerably more successful, and achieved an F1 score of 0.528 over the development set.

`PCL` `Patronizing` `Condescending` `Language`

### 3. [PaperFormalizer: Author-in-the-Loop Autoformalization of Research Papers in Lean](https://arxiv.org/abs/2610.31810)
<sub>arXiv cs.AI · 10-26 12:00</sub>

Starting from the LaTeX source, PaperFormalizer transcribes the paper into a dependency graph of statements, audits each statement in natural language for faithfulness, ambiguity and correctness, and then formalizes and proves the statements in Lean against Mathlib, optional domain libraries and the author's personal…

`大模型与 AI 应用` `PaperFormalizer` `Lean` `Papers` `author`

### 4. [TACS-RF: Tool-driven Agentic Circuit Synthesis of RF and mmWave Modules](https://arxiv.org/abs/2610.31882)
<sub>arXiv cs.AI · 10-26 12:00</sub>

We present the framework of TACS-RF - a Tool-driven Agentic Circuit Synthesis of RF and mmWave modules. We describe the agent-driven design flow and the resulting division of labor between human and agent, taking a step toward a "text-to-ASIC" future for designing RF/mmWave hardware.

`大模型与 AI 应用` `GHz` `TACS-RF` `Tool-driven` `Agentic`

### 5. [$M^3$: A Multi-LLM System for Multi-Turn Jailbreaking as a Markov Decision Process](https://arxiv.org/abs/2610.31937)
<sub>arXiv cs.AI · 10-26 12:00</sub>

Modern Large Language Models (LLMs) remain vulnerable to carefully orchestrated multi-turn interactions that progressively bypass safety mechanisms. We address this gap by introducing $M^3$, an automated red-teaming framework that formalizes multi-turn jailbreaking as a finite-horizon Markov Decision Process (MDP).

`大模型与 AI 应用` `ASR` `LLM` `Markov` `Decision`

### 6. [CEMIR vs. FISER: a comparative study of reasoning-based and enrichment-based approaches to pragmatic intent recognition](https://arxiv.org/abs/2610.32022)
<sub>arXiv cs.AI · 10-26 12:00</sub>

In this paper, we present a comparative and diagnostic study benchmarking FISER - a framework utilizing structured social and embodied reasoning - against CEMIR (Context-Enriched Multimodal Intent Recognition), a method that performs multimodal enrichment by synthesizing narratives and photorealistic images from…

`大模型与 AI 应用` `CEMIR` `FISER` `Intent` `multimodal`

## 开发者工具与基础设施（2）

### 1. [PaperPilot – Zero-Cloud, Pure-Rust PDF Engine with WASM and MCP](https://github.com/KrushnaVardhanReddy/PaperPilot)
<sub>Hacker News 首页 · 10-26 11:29 · HN 159 分</sub>

CLI, MCP, REST, WASM, and desktop share the same Rust core, so behavior is consistent. - Small and dependency-light. It includes the CLI, MCP server, REST gateway, WASM engine, and desktop app.

`PDF` `Rust` `MCP` `WASM`

### 2. [Show HN: ADRs for AI – Deliberation records for human–AI work, versioned in Git](https://adrs.systems)
<sub>Hacker News 首页 · 10-25 08:43 · HN 49 分</sub>

Read about it and tell me # if you accept, or any pushback." Then dump your thinking into a first seed — dictation is fine; your AI chunks it into ADRs that keep your actual words, the options, the reasoning, the open questions. Every question is findable by one grep — ### QST: — or surfaced by the editor extension,…

`Git` `Bitemporal` `Correct` `GPT`

---
本日报由 [news-digest](https://github.com/zhangyan560/news-digest) 自动生成；版权归原作者所有，摘要仅供索引，请点击原文阅读全文。