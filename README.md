# 智能学习助手 —— 基于 LangChain 的智能应用

> 课程作业 · 第七章 智能应用开发
>
> 开源仓库：<https://github.com/508435139/langchain-mini-assistant>

## 一、项目简介

本项目是一个基于 **LangChain** 框架、调用**在线大模型**（DeepSeek，OpenAI 兼容接口）的网页版「智能学习助手」。

用户在浏览器里像聊天一样提问（例如"什么是 LangChain 的 Chain""帮我讲讲进程和线程的区别"），助手扮演计算机课程助教，用中文给出结论、理由和可直接运行的代码，并且能记住前几轮对话内容，支持追问。

整个应用用一条 LangChain 链（LCEL）完成"提示词模板 → 大模型 → 输出解析"的编排，主程序不到 100 行，结构清晰，便于二次修改。

## 二、功能

1. **多轮对话**：把历史消息放进 `MessagesPlaceholder`，模型能理解上下文（如"那它和 Agent 有什么区别？"）。
2. **流式输出**：模型边生成边显示，等待感更小。
3. **角色设定**：System Prompt 把模型约束为"耐心、严谨的课程助教"，回答风格统一。
4. **一键清空**：侧边栏按钮即可重置会话。
5. **模型可替换**：模型名与接口地址都在 `.env` 中配置，改两行即可换成通义、智谱或本地 Ollama。

## 三、技术栈

| 层次 | 选型 | 说明 |
| --- | --- | --- |
| 应用框架 | LangChain 1.4（langchain-core + langchain-openai） | 提示词模板、消息管理、LCEL 链式编排 |
| 大模型 | DeepSeek deepseek-chat | 在线模型，OpenAI 兼容接口 |
| 界面 | Streamlit 1.58 | 聊天组件与流式渲染 |
| 配置 | python-dotenv | 从 .env 读取密钥，避免硬编码 |

## 四、系统结构

核心链只有三环：

```
用户输入
   │
   ▼
ChatPromptTemplate（system 人设 + 历史消息 + 当前问题）
   │
   ▼
ChatOpenAI（deepseek-chat，流式）
   │
   ▼
StrOutputParser → 逐字返回页面
```

- `app.py` 中的 `build_chain()` 负责组装这条链；
- `st.session_state.messages` 保存全部对话，每次提问时把之前的消息转换成 LangChain 的
  `HumanMessage` / `AIMessage` 塞进 `history`，从而实现多轮记忆；
- 页面用 `st.write_stream` 消费流式结果，边生成边渲染。

## 五、目录结构

```
langchain-mini-assistant/
├── app.py            # 主程序：Streamlit 页面 + LangChain 链
├── check.py          # 命令行冒烟测试：不启动网页也能验证模型是否可用
├── requirements.txt  # 依赖清单
├── .env.example      # 配置模板（复制为 .env 后填密钥）
├── .gitignore        # 排除 .env、缓存等
└── README.md
```

## 六、运行步骤

### 1. 环境要求

Python 3.9 及以上。

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置密钥

```bash
# Windows
copy .env.example .env
# macOS / Linux
cp .env.example .env
```

编辑 `.env`，填入自己的密钥（DeepSeek 或其他 OpenAI 兼容服务）：

```ini
OPENAI_API_KEY=sk-你的密钥
OPENAI_API_BASE=https://api.deepseek.com
MODEL_NAME=deepseek-chat
```

> `.env` 已在 `.gitignore` 中，不会被提交到仓库。

### 4. 启动网页

```bash
streamlit run app.py
```

浏览器打开 <http://localhost:8501>，在底部输入框提问即可。

### 5. 命令行验证（可选）

不打开网页时，可以用一行命令确认配置是否正确：

```bash
python check.py "用一句话说明 LangChain 解决了什么问题"
```

## 七、使用示例

启动后在输入框中提问即可，典型的提问方式：

- 概念解释类："什么是 LangChain 的 Chain？它和 Agent 有什么区别？"
- 代码求助类："用 Python 写一个快速排序，并逐行解释。"
- 追问类：先问"什么是死锁"，再问"那怎么避免？"，助手会结合上一轮回答。

回答由模型实时生成，内容与措辞每次可能略有不同。

## 八、说明

- **密钥安全**：密钥只放在本地 `.env`，仓库中仅保留 `.env.example` 模板。
- **切换为离线模型**：把 `.env` 改为本地 Ollama 的 OpenAI 兼容地址即可，代码无需改动：

  ```ini
  OPENAI_API_BASE=http://localhost:11434/v1
  MODEL_NAME=qwen2.5:7b
  OPENAI_API_KEY=ollama
  ```

- **可扩展方向**：如需文档问答，可在链前增加 Retriever 构成 RAG；如需联网检索，可引入 Tool 与 Agent。
