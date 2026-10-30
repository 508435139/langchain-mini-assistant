"""命令行冒烟测试：不启动网页，直接验证 .env 配置与模型调用是否正常。

用法：python check.py [你的问题]
"""

import sys

from app import build_chain

question = sys.argv[1] if len(sys.argv) > 1 else "用一句话说明 LangChain 解决了什么问题。"
print(f"[问] {question}")
answer = build_chain().invoke({"history": [], "question": question})
print(f"[答] {answer}")
