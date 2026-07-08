# MetaMAVS 迁移指南：Claude → 本地 Gemma 4 (llama-server)

> **目的**：把 MetaMAVS 多智能体系统中所有对 Claude / Anthropic 的模型调用，
> 迁移为调用本地部署的 Gemma 4 E2B 模型（通过 llama.cpp 的 llama-server，
> 走 OpenAI 兼容协议）。业务逻辑（LangGraph 图、agent 节点、工具）尽量不动。
>
> **交接对象**：Claude Code
> **系统**：MetaMAVS（宏基因组病毒检测多智能体系统，基于 LangGraph）
> **作者**：sihua

---

## 0. 一句话背景

本地已用 llama.cpp 的 **llama-server** 部署好 `gemma-4-E2B-it`（GGUF, Q8_0），
它对外暴露一个 **OpenAI 兼容** 的 HTTP 接口。因此在 Python 里可以直接用
任何 OpenAI 兼容客户端（如 `langchain-openai` 的 `ChatOpenAI`）连接它，
**无需 `llama-cpp-python`、无需 Ollama、无需 `langchain-community`**。

这套方案已在一个独立的搜索 agent 应用中验证可用（连接、工具调用、多轮对话均正常）。

---

## 1. 本地 Gemma 环境规格（Claude Code 需要知道的事实）

| 项目 | 值 |
|------|----|
| 模型 | `gemma-4-E2B-it`（多模态，能看图；GGUF Q8_0）|
| 服务程序 | llama.cpp 的 `llama-server` |
| Endpoint | `http://localhost:8080/v1`（OpenAI 兼容）|
| API Key | 不校验，填任意非空字符串（如 `"not-needed"`）|
| model 参数名 | `gemma-4-E2B-it` |
| 上下文长度 | 32768（启动参数 `-c 32768`）|
| 关键启动参数 | **`--jinja`**（缺了工具调用/function calling 解析不出来）|
| llama.cpp 目录 | `/home/sihua/Gemma_4_E2B-it/llama.cpp/` |

### llama-server 启动命令（供参考，通常已在运行）

```bash
cd /home/sihua/Gemma_4_E2B-it/llama.cpp
./build/bin/llama-server \
  -hf ggml-org/gemma-4-E2B-it-GGUF \
  --host 0.0.0.0 --port 8080 \
  -ngl 99 \
  -c 32768 \
  --jinja
```

### 健康检查（迁移前先确认服务在跑）

```bash
# 看进程
ps aux | grep llama-server | grep -v grep

# 测接口（OpenAI 兼容的 /v1/models）
curl http://localhost:8080/v1/models
```

---

## 2. 迁移的核心原理

MetaMAVS 里所有 agent / 节点最终都依赖一个 **LLM 客户端对象**。
只要把「构造这个对象」的那几行从 Anthropic 换成指向本地 endpoint 的 OpenAI 客户端，
**上层 LangGraph 图结构、agent 逻辑、工具定义、prompt 都无需改动**——
因为它们面对的是一个抽象的 `llm` 接口，不关心底层是 Claude 还是 Gemma。

```
[LangGraph 图 / agents / tools]   ← 不动
              ↓ 依赖
        llm 客户端对象            ← 只改这里
              ↓ 连接
   Claude API  →  本地 llama-server
```

---

## 3. 需要 Claude Code 执行的迁移步骤

### 步骤 1：全局搜索所有 Claude / Anthropic 调用点

在 MetaMAVS 代码库里搜索这些关键字，列出所有命中文件与行号：

```
ChatAnthropic
langchain_anthropic
anthropic
Anthropic
claude-            # 如 claude-3-5-sonnet / claude-opus 等 model 字符串
ANTHROPIC_API_KEY
```

请先产出一张「调用点清单」（文件 : 行号 : 当前写法），再动手改。

### 步骤 2：按调用方式分类改写

MetaMAVS 可能用了以下任意一种或多种方式，分别处理：

#### 情况 A：LangChain 的 `ChatAnthropic`（最常见）

**改前：**
```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    temperature=0.3,
    api_key=os.environ["ANTHROPIC_API_KEY"],
)
```

**改后：**
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    base_url="http://localhost:8080/v1",
    api_key="not-needed",          # llama-server 不校验
    model="gemma-4-E2B-it",
    temperature=0.3,
)
```

> 其余参数（temperature、max_tokens 等）保持原值即可。
> `ChatOpenAI` 与 `ChatAnthropic` 在 LangChain 里是同一套接口，
> `.invoke()` / `.bind_tools()` / 在 LangGraph 节点中的用法都一致。

#### 情况 B：Anthropic 官方 SDK（`from anthropic import Anthropic`）

如果代码直接用官方 SDK，有两种选择：

**选择 B1（推荐，改动小）**：改用 `openai` SDK 指向本地
```python
# 改前
# from anthropic import Anthropic
# client = Anthropic(api_key=...)
# resp = client.messages.create(model="claude-...", messages=[...])

# 改后
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8080/v1", api_key="not-needed")
resp = client.chat.completions.create(
    model="gemma-4-E2B-it",
    messages=[...],          # 注意：OpenAI 的 messages 格式，见下方注意事项
)
# 取回复：resp.choices[0].message.content
```

> ⚠️ Anthropic SDK 和 OpenAI SDK 的 **请求/响应结构不同**：
> - Anthropic：`client.messages.create(...)`，`system` 是独立参数，回复在 `resp.content[0].text`
> - OpenAI：`client.chat.completions.create(...)`，`system` 作为 messages 里 role=system 的一条，回复在 `resp.choices[0].message.content`
> 需要 Claude Code 逐处对齐这两种格式。

**选择 B2**：统一改用 LangChain 的 `ChatOpenAI`（同情况 A），
让整个项目的 LLM 调用风格统一。若 MetaMAVS 已大量使用 LangChain，推荐这条。

### 步骤 3：处理 model 字符串常量

如果项目里有集中定义的模型名常量（如 `MODEL = "claude-3-5-sonnet-..."`），
统一改成 `"gemma-4-E2B-it"`。搜索所有 `claude-` 开头的字符串。

### 步骤 4：工具调用 / function calling 检查

MetaMAVS 若用了工具调用（bind_tools / ReAct agent / 结构化输出），迁移后**必须实测**：

- llama-server **必须带 `--jinja` 启动**，否则工具调用无法解析。
- Gemma 4 E2B 是**小模型**，function calling 的稳定性与准确性**弱于 Claude**。
  复杂的多工具、多步 agent 可能出现：调错工具、参数格式不对、不调用工具直接乱答。
- 建议迁移后对每个 agent 节点单独跑测试，观察工具调用是否正常。

### 步骤 5：环境变量与配置清理

- `ANTHROPIC_API_KEY` 不再需要（可保留，不影响；或从 .env / config 移除）。
- 若有 `requirements.txt` / `pyproject.toml`，可保留 `langchain-anthropic`（不冲突），
  确保安装了 `langchain-openai`。

---

## 4. 迁移后验证清单

Claude Code 完成改动后，请按此清单逐项验证：

- [ ] `curl http://localhost:8080/v1/models` 能返回模型信息（服务在跑）
- [ ] 单点冒烟测试：随便找一个用到 llm 的节点，`llm.invoke("hello")` 能正常返回
- [ ] 各 agent 节点逐个跑通，无 import / 连接错误
- [ ] 用到工具调用的节点，工具能被正确触发（确认 llama-server 带了 `--jinja`）
- [ ] 端到端跑一次 MetaMAVS 主流程（哪怕用小样本），确认图能走完
- [ ] 对比迁移前后输出：Gemma 的结果质量是否可接受（见下方「预期差异」）

---

## 5. 预期差异与风险（重要，务必告知用户）

从 Claude 迁移到 Gemma 4 E2B，**能跑通 ≠ 效果等同**。E2B 是小参数模型，请预期：

| 维度 | 变化 |
|------|------|
| 推理深度 / 复杂指令遵循 | ⬇️ 明显弱于 Claude，长而复杂的 prompt 可能遵循不全 |
| 工具调用稳定性 | ⬇️ 多工具、多步 ReAct 更容易出错 |
| 长上下文处理 | ⬇️ 32K 上限，且小模型对长文实际利用率有限 |
| 结构化输出（JSON 等）| ⚠️ 可能格式不稳，需加严格 prompt 或后处理校验 |
| 中文/多语言 | ✅ 尚可 |
| 速度 / 成本 | ⬆️ 本地推理、零 API 费用、数据不出本地（对科研敏感数据是优势）|

**建议策略**：
1. 先整体迁移跑通，定位哪些 agent 节点对模型能力最敏感。
2. 对能力敏感的节点，可考虑：简化 prompt、拆分任务、加输出校验/重试，
   或（若条件允许）换更大的本地模型（改 `-hf` 拉更大 GGUF，`model` 名相应调整）。
3. `ChatOpenAI(base_url=...)` 这套写法的好处：将来想换回 Claude 或换别的模型，
   只改构造那几行即可，图逻辑不动。

---

## 6. 回滚方案

保留原有 `ChatAnthropic` 代码于版本控制中（git）。若 Gemma 效果不达标，
`git revert` 或用配置开关在两者间切换。可考虑做成配置项：

```python
# 示意：用环境变量切换后端，便于 A/B 对比
import os
from langchain_openai import ChatOpenAI

def get_llm(temperature=0.3):
    backend = os.getenv("LLM_BACKEND", "gemma")
    if backend == "gemma":
        return ChatOpenAI(
            base_url="http://localhost:8080/v1",
            api_key="not-needed",
            model="gemma-4-E2B-it",
            temperature=temperature,
        )
    elif backend == "claude":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=temperature,
        )
    raise ValueError(f"unknown LLM_BACKEND: {backend}")
```

这样一处封装，全项目统一调用 `get_llm()`，切换后端只需改环境变量 `LLM_BACKEND`。
**推荐 Claude Code 优先落地这个封装函数**，再把项目中所有 llm 构造点替换为 `get_llm()`。

---

## 7. 给 Claude Code 的执行顺序建议

1. 先跑健康检查（§1），确认 llama-server 在 8080 正常。
2. 全局搜索列出所有 Claude 调用点（§3 步骤1），产出清单给用户确认。
3. 实现 §6 的 `get_llm()` 封装函数。
4. 把所有调用点替换为 `get_llm()`（默认走 gemma）。
5. 按 §4 清单逐项验证。
6. 向用户报告：哪些节点跑通、哪些节点质量存疑、建议后续如何优化。

---

*本指南由 sihua 在与 Claude（chat）协作搭建本地 Gemma 环境后整理，用于交接给 Claude Code 执行 MetaMAVS 的模型迁移。*
