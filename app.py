"""第七章 智能应用开发 —— 基于 LangChain 的「智能学习助手」

Streamlit 网页界面 + LangChain 链式编排 + OpenAI 兼容接口的大模型，
支持多轮对话记忆、流式输出。
"""

import os

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-chat")
API_BASE = os.getenv("OPENAI_API_BASE", "https://api.deepseek.com")
API_KEY = os.getenv("OPENAI_API_KEY", "")

SYSTEM_PROMPT = (
    "你是一名耐心、严谨的大学计算机课程助教。"
    "请用中文回答：先给结论，再给理由或步骤；涉及代码时给出可直接运行的完整示例，"
    "并解释关键行。不确定的内容要明确说明，不要编造。"
)


def build_chain():
    """组装 LangChain 链：提示词模板 -> 大模型 -> 文本输出解析。"""
    llm = ChatOpenAI(
        model=MODEL_NAME,
        api_key=API_KEY,
        base_url=API_BASE,
        temperature=0.3,
        streaming=True,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("history"),
            ("human", "{question}"),
        ]
    )
    return prompt | llm | StrOutputParser()


def to_lc_messages(history):
    """把 session_state 里的字典历史转成 LangChain 的消息对象。"""
    return [
        HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"])
        for m in history
    ]


def main():
    st.set_page_config(page_title="智能学习助手", page_icon="🎓", layout="centered")

    st.title("🎓 智能学习助手")
    st.caption(f"LangChain + {MODEL_NAME} ｜ 支持多轮对话")

    with st.sidebar:
        st.subheader("使用说明")
        st.markdown("1. 在下方输入框提问\n2. 助手会记住上下文\n3. 可随时清空对话")
        if st.button("清空对话", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        st.divider()
        st.caption(f"模型：{MODEL_NAME}")
        st.caption(f"接口：{API_BASE}")

    if not API_KEY:
        st.error("未检测到 OPENAI_API_KEY，请先在项目根目录创建 .env 文件（参考 .env.example）。")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("输入你的问题，例如：什么是 LangChain 的 Chain？")
    if not question:
        return

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    history = to_lc_messages(st.session_state.messages[:-1])
    with st.chat_message("assistant"):
        try:
            answer = st.write_stream(build_chain().stream({"history": history, "question": question}))
        except Exception as exc:  # 网络 / 密钥 / 额度等异常统一提示
            answer = f"调用模型失败：{exc}"
            st.error(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
