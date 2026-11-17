
import os
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ==============================
# 1. 基本配置
# ==============================

load_dotenv()

st.set_page_config(
    page_title="配电网自动化技术智能体",
    page_icon="⚡",
    layout="wide"
)

MODEL_NAME = "gemini-3.5-flash"

# ==============================
# 2. API 配置
# ==============================

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("未找到 Gemini API Key，请检查 Secrets 配置。")
    st.stop()

client = genai.Client(api_key=api_key)

# ==============================
# 3. 页面样式
# ==============================

st.markdown("""
<style>
.stApp {
    background-color: #0b1220;
    color: #e5e7eb;
}

section[data-testid="stSidebar"] {
    background-color: #111c30;
}

.main-title {
    font-size: 32px;
    font-weight: 700;
    color: #60a5fa;
    text-align: center;
    margin-bottom: 8px;
}

.sub-title {
    color: #94a3b8;
    text-align: center;
    font-size: 15px;
    margin-bottom: 30px;
}

.answer-box {
    background-color: #142238;
    border: 1px solid #263b59;
    border-radius: 12px;
    padding: 20px;
    min-height: 180px;
}

.answer-title {
    color: #60a5fa;
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 15px;
}

.stButton button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    border: none;
    font-weight: bold;
}

.stButton button:hover {
    background-color: #1d4ed8;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# 4. 侧边栏
# ==============================

with st.sidebar:
    st.markdown("## ⚡ 配电网 AI 助手")
    st.markdown("---")

    st.markdown("### 系统信息")

    # 调试信息：检查实际运行的模型
    st.write("DEBUG MODEL:", MODEL_NAME)

    st.caption("AI 模型：" + MODEL_NAME)
    st.caption("系统版本：1.0")

    st.markdown("---")

    st.markdown("### 功能介绍")
    st.write("💬 智能问答")
    st.write("📷 图片题目求解")

    st.markdown("---")
    st.caption("配电网自动化技术智能体")

# ==============================
# 5. 页面标题
# ==============================

st.markdown(
    '<div class="main-title">⚡ 配电网自动化技术智能体</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'Distribution Network Automation AI Assistant'
    '</div>',
    unsafe_allow_html=True
)

# ==============================
# 6. AI 请求函数
# ==============================

def generate_with_retry(contents, max_retries=3):

    last_error = None

    for attempt in range(max_retries):

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents
            )

            if not response or not response.text:
                raise Exception("AI 未返回有效内容，请重新尝试。")

            return response.text

        except Exception as e:

            last_error = e
            error_message = str(e)
            error_upper = error_message.upper()

            # 每日免费额度耗尽，不进行无意义重试
            if (
                "GENERATEREQUESTSPERDAY" in error_upper
                or "PER DAY" in error_upper
                or "QUOTA EXCEEDED" in error_upper
            ):
                raise Exception(
                    "Gemini API 免费每日请求额度已用完。\n\n"
                    "请等待额度重置，或检查 Google AI Studio 的配额。\n\n"
                    f"原始错误：{error_message}"
                )

            # 判断是否属于临时错误
            retryable = (
                "503" in error_upper
                or "UNAVAILABLE" in error_upper
                or "500" in error_upper
                or "INTERNAL" in error_upper
                or "DEADLINE_EXCEEDED" in error_upper
            )

            if not retryable or attempt == max_retries - 1:
                break

            wait_time = 2 ** (attempt + 1)

            st.warning(
                f"服务器暂时繁忙，第 {attempt + 1} 次请求失败，"
                f"将在 {wait_time} 秒后重试。"
            )

            time.sleep(wait_time)

    raise Exception(
        f"Gemini API 请求失败，共尝试 {max_retries} 次。\n\n"
        f"原始错误：{last_error}"
    )

# ==============================
# 7. 双语答案处理
# ==============================

def display_bilingual_answer(answer):

    chinese_answer = ""
    vietnamese_answer = ""

    if "【中文回答】" in answer and "【越南语回答】" in answer:

        parts = answer.split("【越南语回答】", 1)

        chinese_answer = parts[0].replace(
            "【中文回答】", ""
        ).strip()

        vietnamese_answer = parts[1].strip()

    else:
        chinese_answer = answer
        vietnamese_answer = (
            "AI 未能按照指定格式分开回答，"
            "请查看左侧原始回答。"
        )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="answer-box">',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="answer-title">🇨🇳 中文回答</div>',
            unsafe_allow_html=True
        )
        st.markdown(chinese_answer)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(
            '<div class="answer-box">',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="answer-title">🇻🇳 越南语回答</div>',
            unsafe_allow_html=True
        )
        st.markdown(vietnamese_answer)
        st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# 8. 回答格式要求
# ==============================

def make_prompt(question):

    return f"""
你是一名专业的配电网自动化技术专家和大学教师。

请认真回答用户的问题：

{question}

回答要求：

1. 使用简体中文和越南语回答。
2. 中文和越南语内容必须保持一致。
3. 先解释基本概念，再解释工作原理。
4. 如果涉及计算题，必须列出公式、代入过程和最终答案。
5. 如果涉及电路、电力系统或自动化设备，
   应尽可能解释其物理原理。
6. 内容准确、清晰，适合大学电气工程专业学生学习。
7. 不要编造数据或不存在的公式。

请严格按照以下格式回答：

【中文回答】
这里写完整的简体中文答案。

【越南语回答】
这里写完整的越南语答案。
"""

# ==============================
# 9. 功能选项卡
# ==============================

tab1, tab2 = st.tabs([
    "💬 智能问答",
    "📷 图片题目求解"
])

# ==============================
# 10. 智能问答
# ==============================

with tab1:

    st.subheader("💬 配电网自动化智能问答")

    question = st.text_area(
        "请输入您的问题：",
        placeholder="例如：什么是配电网自动化？",
        height=130,
        key="text_question"
    )

    if st.button("🚀 提交问题", key="ask_button"):

        if not question.strip():
            st.warning("请先输入问题。")

        else:

            with st.spinner("AI 正在思考，请稍候..."):

                try:
                    prompt = make_prompt(question)

                    answer = generate_with_retry(prompt)

                    st.success("回答完成！")

                    display_bilingual_answer(answer)

                except Exception as e:
                    st.error("AI 请求失败")
                    st.code(str(e))

# ==============================
# 11. 图片题目求解
# ==============================

with tab2:

    st.subheader("📷 上传图片，自动识别并解答题目")

    uploaded_file = st.file_uploader(
        "请选择题目图片：",
        type=["png", "jpg", "jpeg"],
        help="支持 PNG、JPG 和 JPEG 格式"
    )

    if uploaded_file is not None:

        st.image(
            uploaded_file,
            caption="已上传的题目图片",
            use_container_width=True
        )

        if st.button("🔍 识别并解答", key="image_button"):

            with st.spinner("AI 正在识别图片并解答..."):

                try:
                    image_bytes = uploaded_file.getvalue()

                    image_part = types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=uploaded_file.type
                    )

                    image_prompt = """
你是一名专业的配电网自动化技术教师。

请识别图片中的题目，并完成以下任务：

1. 准确提取图片中的题目内容。
2. 分析题目要求。
3. 给出详细解题步骤。
4. 如果涉及计算，写出公式、代入过程和最终答案。
5. 如果涉及电路图，请分析电路结构和工作原理。
6. 使用简体中文和越南语回答。
7. 两种语言的内容必须一致。

请严格按照以下格式：

【中文回答】
题目识别结果、分析过程和完整答案。

【越南语回答】
题目识别结果、分析过程和完整答案。
"""

                    answer = generate_with_retry([
                        image_prompt,
                        image_part
                    ])

                    st.success("图片识别与解答完成！")

                    display_bilingual_answer(answer)

                except Exception as e:
                    st.error("图片识别或解答失败")
                    st.code(str(e))

# ==============================
# 12. 页面底部
# ==============================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center;color:#64748b;font-size:13px;">
        配电网自动化技术智能体 | Powered by Gemini API
    </div>
    """,
    unsafe_allow_html=True
)
