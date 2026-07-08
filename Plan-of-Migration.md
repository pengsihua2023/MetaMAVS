# Plan of Migration: Claude → Local Gemma 4 E2B

**目标**：将 MetaMAVS 中所有 Claude/Anthropic API 调用迁移为本地 Gemma 4 E2B（通过 llama-server）  
**优先级**：确保迁移后功能可用 → 验证质量 → 优化性能  
**总体策略**：中心化 LLM 客户端构造，最小化业务逻辑改动  

---

## 阶段 0：迁移前准备与调查（1-2 小时）

### Task 0.1：确认本地 Gemma 环境就绪

- [ ] 运行健康检查
  ```bash
  ps aux | grep llama-server | grep -v grep
  curl http://localhost:8080/v1/models
  ```
- [ ] 验证 llama-server 启动参数包含 `--jinja`（工具调用必需）
- [ ] 记录 endpoint 信息：
  - Endpoint: `http://localhost:8080/v1`
  - Model ID: `gemma-4-E2B-it`
  - API Key: 任意非空字符串（如 `"not-needed"`）

**验收标准**：
- `curl http://localhost:8080/v1/models` 返回 200 + 模型列表
- llama-server 进程正在运行，无错误日志

---

### Task 0.2：全局搜索与清单

在 MetaMAVS 代码库中搜索所有 Claude/Anthropic 调用点，产出《调用点清单》

**搜索关键字**：
```
ChatAnthropic
langchain_anthropic
anthropic
Anthropic
claude-              (模型字符串如 claude-3-5-sonnet)
ANTHROPIC_API_KEY
from anthropic import
```

**输出**：清单文件 `MIGRATION_CALLSITES.txt`（格式：文件:行号:当前代码片段）

**验收标准**：
- 列出每个调用点的文件、行号、当前代码
- 分类标记：LangChain ChatAnthropic / 官方 SDK / 其他
- 清单完整性由代码搜索+手工审查确认

---

### Task 0.3：分析项目依赖与导入

- [ ] 检查 `pyproject.toml` 和 `requirements.txt`
  - 确认已安装 `langchain-anthropic`
  - 确认已安装 `langchain-openai`（若未安装，后续需加入）
  - 检查 LangGraph 版本兼容性
- [ ] 列出所有 import 本地 agent 模块的文件
- [ ] 确认是否有环境变量文件（`.env` / `.env.local`）使用 `ANTHROPIC_API_KEY`

**验收标准**：
- 依赖清单已列出
- 确认 `langchain-openai` 可用（或需要在步骤 1 中加入）

---

## 阶段 1：实现 LLM 工厂函数（1-2 小时）

### Task 1.1：创建 `metamavs/config/llm_factory.py`

新建 LLM 构造工厂函数，支持 Gemma / Claude 切换

```python
# metamavs/config/llm_factory.py
import os
from langchain_openai import ChatOpenAI
from typing import Optional

def get_llm(temperature: float = 0.3, model: Optional[str] = None) -> ChatOpenAI:
    """
    构造 LLM 客户端（支持后端切换）。
    
    环境变量 LLM_BACKEND 控制后端：
    - "gemma"（默认）：本地 llama-server
    - "claude"：Anthropic Claude（需设置 ANTHROPIC_API_KEY）
    """
    backend = os.getenv("LLM_BACKEND", "gemma").lower()
    
    if backend == "gemma":
        return ChatOpenAI(
            base_url="http://localhost:8080/v1",
            api_key="not-needed",
            model=model or "gemma-4-E2B-it",
            temperature=temperature,
        )
    elif backend == "claude":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model or "claude-3-5-sonnet-20241022",
            temperature=temperature,
        )
    else:
        raise ValueError(f"Unknown LLM_BACKEND: {backend}. Use 'gemma' or 'claude'.")
```

**验收标准**：
- 文件创建成功
- 函数能被 import（快速 `python -c "from metamavs.config.llm_factory import get_llm; print(get_llm())"`）
- 默认返回 Gemma 客户端

---

### Task 1.2：单点冒烟测试

- [ ] 测试 Gemma 后端
  ```python
  from metamavs.config.llm_factory import get_llm
  llm = get_llm(temperature=0.3)
  result = llm.invoke("Hello, reply with one word.")
  print(result.content)
  ```
- [ ] 测试 Claude 后端（可选，仅验证兼容性）
  ```bash
  LLM_BACKEND=claude python -c "from metamavs.config.llm_factory import get_llm; ..."
  ```

**验收标准**：
- Gemma 后端能成功调用并返回文本
- 无 import 或连接错误

---

## 阶段 2：调用点迁移（3-4 小时）

### Task 2.1：迁移 LangChain ChatAnthropic 调用（最常见）

按照清单逐个替换所有 `ChatAnthropic` 构造调用为 `get_llm()` 调用

**模式**：
```python
# 改前
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.3)

# 改后
from metamavs.config.llm_factory import get_llm
llm = get_llm(temperature=0.3)
```

**文件范围**（基于清单）：
- 各 agent 模块（`metamavs/agents/*.py`）
- 工具定义模块
- 任何直接构造 LLM 的地方

**验收标准**：
- 所有 ChatAnthropic import 已移除或改为 get_llm
- 没有硬编码的 claude-* 模型字符串（除非在 llm_factory.py 中）
- 清单中的所有调用点都已处理

---

### Task 2.2：处理官方 Anthropic SDK 调用（如有）

若发现 `from anthropic import Anthropic` 或 `from anthropic import messages` 的调用：

**优先选择**：改用 LangChain 的 `ChatOpenAI`（通过 get_llm）
```python
# 改前
from anthropic import Anthropic
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
resp = client.messages.create(model="claude-...", messages=[...])

# 改后
from metamavs.config.llm_factory import get_llm
llm = get_llm()
result = llm.invoke("...")  # or bind_tools / 其他 LangChain 方法
```

若无法用 LangChain 适配，可直接改用 OpenAI SDK：
```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8080/v1", api_key="not-needed")
resp = client.chat.completions.create(
    model="gemma-4-E2B-it",
    messages=[...],
)
```

**验收标准**：
- 清单中所有官方 SDK 调用都已改写或标记为 N/A
- 格式转换（Anthropic SDK → OpenAI SDK）正确（messages 结构、回复字段等）

---

### Task 2.3：更新环境变量与配置

- [ ] 检查项目中是否有 `.env` / `.env.local` / `config.yaml`，移除或注释 `ANTHROPIC_API_KEY`
- [ ] 若项目有配置文件，确认 LLM 后端配置已支持 `LLM_BACKEND` 环境变量
- [ ] 更新 `pyproject.toml` / `requirements.txt`（若需要）：
  - 保留 `langchain-anthropic`（不冲突，向后兼容）
  - 确保 `langchain-openai` 已在依赖列表中

**验收标准**：
- 无 ANTHROPIC_API_KEY 依赖（或是可选的）
- 环境变量清晰文档化（README 说明 LLM_BACKEND 用法）

---

## 阶段 3：验证与测试（2-3 小时）

### Task 3.1：模块级导入测试

逐个验证各 agent 模块能被导入

```bash
python -c "from metamavs.agents.qc_agent import qc_agent_node"
python -c "from metamavs.agents.host_removal_agent import host_removal_agent_node"
# ... 逐个验证所有 agent
```

**验收标准**：
- 所有 agent 模块导入成功
- 无 ImportError 或 AttributeError

---

### Task 3.2：各 Agent 节点单点测试

针对使用工具调用（bind_tools / ReAct）的节点，逐个实测

**典型测试模式**：
```python
from metamavs.state import MetaMAVSState
from metamavs.agents.some_agent import some_agent_node
from metamavs.config.llm_factory import get_llm

# 构造最小状态
state = {
    "config": {"dry_run": True},
    "run_id": "test_run_001",
    # ... 其他必需字段
}

# 运行节点
try:
    result = some_agent_node(state)
    print("✓ Node ran successfully")
    print(f"  Output keys: {result.keys()}")
except Exception as e:
    print(f"✗ Node failed: {e}")
```

**关键检查点**：
- [ ] 无连接错误（llm client 能连上 llama-server）
- [ ] 工具调用节点能正确触发工具
- [ ] 输出字段符合预期
- [ ] dry-run 模式工作正常

**验收标准**：
- 至少 80% 的 agent 节点能正常运行
- 工具调用节点工具被正确触发（检查日志或返回值）
- 无格式错误（如期望 JSON 但得到乱码）

---

### Task 3.3：端到端流程测试

用示例配置 + 小规模样本数据跑一遍完整流程

```bash
metamavs run --config configs/example_config.yaml --dry-run
```

或（若已有更复杂的测试）：
```bash
pytest tests/ -v
```

**关键观测点**：
- [ ] 图能走完（不卡死）
- [ ] 中间输出文件生成正常
- [ ] 最终报告（Markdown / HTML）能成功生成
- [ ] 日志无关键错误

**验收标准**：
- 流程运行完毕（status = SUCCESS 或 COMPLETED）
- 输出目录结构正确
- 报告文件能打开（Markdown 可读，HTML 能浏览）

---

### Task 3.4：模型质量初步评估

对比迁移前后的输出，评估质量差异

**评估维度**：
- 分类准确性（taxonomy classification）：Gemma 输出是否有明显偏差？
- 工具调用稳定性：是否有频繁的工具调用失败或参数错误？
- 文本质量：reports / risk assessment 是否可读、逻辑通顺？
- 速度：推理时间是否在可接受范围内？

**预期**：Gemma 会略弱于 Claude，但基本功能应可用

**验收标准**：
- 能运行完整流程
- 关键节点的输出质量可接受（允许有质量差异，但不能完全错误）

---

## 阶段 4：文档与交接（0.5-1 小时）

### Task 4.1：更新 README 和使用文档

在 `README.md` 中添加部分：

```markdown
## LLM 后端配置

MetaMAVS 支持多个 LLM 后端，通过环境变量 `LLM_BACKEND` 切换：

### Gemma 4 E2B（默认，本地）

```bash
export LLM_BACKEND=gemma
metamavs run --config configs/example_config.yaml
```

要求：llama-server 运行在 `http://localhost:8080/v1`（含 `--jinja` 参数）

### Claude（需 Anthropic API Key）

```bash
export LLM_BACKEND=claude
export ANTHROPIC_API_KEY=sk-ant-...
metamavs run --config configs/example_config.yaml
```

### 迁移注意事项

- Gemma 4 E2B 是小参数模型，工具调用稳定性低于 Claude
- 长文本处理能力受限（32K context 上限）
- 复杂推理节点建议验证输出质量
- 若质量不达标，可切换回 Claude 后端或升级为更大的本地模型
```

### Task 4.2：创建迁移记录与决策日志

在 `docs/` 或根目录创建 `MIGRATION_LOG.md`，记录：
- 迁移日期
- 改动的文件清单
- 发现的问题与解决方案
- 质量差异说明
- 后续优化建议

---

## 阶段 5：潜在风险与回滚（参考）

### 已知风险

| 风险 | 缓解策略 |
|------|--------|
| Gemma 工具调用失败 | 简化 prompt，加输出验证/重试 |
| 长文本丢失信息 | 拆分大任务，或升级为更大模型 |
| 模型质量差异 | 文档化差异，建议用户评估是否接受 |
| llama-server 意外停止 | 监控服务，添加启动脚本 |

### 回滚方案

若迁移后质量无法接受：

1. **快速回滚**：`git revert` 迁移提交
2. **灰度切换**：保留 `LLM_BACKEND` 开关，默认回到 Claude，待优化后再切回 Gemma

---

## 里程碑与时间估计

| 阶段 | 任务数 | 预计时间 | 完成标志 |
|------|--------|--------|---------|
| 0. 准备 | 3 | 1-2h | 健康检查 + 调用点清单 |
| 1. 工厂函数 | 2 | 1-2h | get_llm() 能导入 + 冒烟测试通过 |
| 2. 迁移调用点 | 3 | 3-4h | 所有 ChatAnthropic 改为 get_llm() |
| 3. 验证测试 | 4 | 2-3h | 端到端流程运行完毕 + 初步质量评估 |
| 4. 文档交接 | 2 | 0.5-1h | README 更新 + 迁移日志 |
| **总计** | **14** | **8-12h** | 迁移完成 + 质量验证通过 |

---

## 执行检查清单

- [ ] Task 0.1：llama-server 健康检查通过
- [ ] Task 0.2：调用点清单完成
- [ ] Task 0.3：依赖分析完成
- [ ] Task 1.1：llm_factory.py 创建
- [ ] Task 1.2：冒烟测试通过
- [ ] Task 2.1：所有 ChatAnthropic 迁移完毕
- [ ] Task 2.2：官方 SDK 调用处理完毕
- [ ] Task 2.3：环境变量与配置更新
- [ ] Task 3.1：模块导入测试通过
- [ ] Task 3.2：agent 节点单点测试通过（80%+）
- [ ] Task 3.3：端到端流程测试通过
- [ ] Task 3.4：质量评估完成
- [ ] Task 4.1：文档更新
- [ ] Task 4.2：迁移日志记录
- [ ] **迁移完成**，可开始生产使用或进一步优化

---

**下一步**：待用户确认本计划，开始执行 Task 0.1（健康检查）。

