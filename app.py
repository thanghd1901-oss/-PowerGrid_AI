
import os
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ==================== 基础配置 ====================

load_dotenv()

st.set_page_config(
    page_title="配电网智能助手",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS ====================

st.markdown("""
<style>
.stApp {
    background-color: #0b1220;
    color: #e5edf7;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111d32, #0b1425);
    border-right: 1px solid #243650;
}

[data-testid="stSidebar"] * {
    color: #dce8f8;
}

.main .block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero {
    background: linear-gradient(120deg, #142b4a, #123e63);
    border: 1px solid #28547a;
    border-radius: 18px;
    padding: 30px;
    margin-bottom: 25px;
}

.hero h1 {
    color: white;
    font-size: 32px;
    margin-bottom: 8px;
}

.hero p {
    color: #b7cce3;
    font-size: 15px;
}

.info-card {
    background: #142137;
    border: 1px solid #263d5b;
    border-radius: 14px;
    padding: 20px;
    min-height: 115px;
}

.info-title {
    color: #91a9c5;
    font-size: 13px;
}

.info-value {
    color: #ffffff;
    font-size: 21px;
    font-weight: 650;
    margin-top: 9px;
}

.section-title {
    color: #e9f3ff;
    font-size: 21px;
    font-weight: 650;
    margin-top: 10px;
    margin-bottom: 15px;
}

.stTextArea textarea {
    background: #111d30 !important;
    color: white !important;
    border: 1px solid #344b69 !important;
    border-radius: 12px !important;
}

.stTextArea textarea:focus {
    border-color: #29a8e0 !important;
}

.stButton > button {
    background: linear-gradient(90deg, #087dbb, #12a5d9);
    color: white;
    border: none;
    border-radius: 9px;
    font-weight: 600;
    min-height: 43px;
    padding: 0 24px;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #0799d7, #25bce9);
    color: white;
    border: none;
}

[data-testid="stFileUploader"] {
    background: #111d30;
    border: 1px dashed #3b668c;
    border-radius: 12px;
    padding: 15px;
}

[data-testid="stFileUploader"] * {
    color: #dce8f8;
}

div[data-testid="stTabs"] button {
    color: #a9bfd8;
    font-weight: 600;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #35b9ed;
}

.answer-box {
    background: #13243a;
    border-left: 4px solid #16a5df;
    border-radius: 8px;
    padding: 18px;
    margin-top: 15px;
}

.footer {
    color: #71869f;
    text-align: center;
    font-size: 12px;
    padding-top: 25px;
}
</style>
""", unsafe_allow_html=True)


# ==================== API 初始化 ====================

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("未找到 API 密钥，请检查 Streamlit Secrets 设置。")
    st.stop()

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.5-flash"


# ==================== AI 请求函数 ====================

def generate_with_retry(contents, max_retries=3):

    for attempt in range(max_retries):

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents
            )

            if not response or not response.text:
                raise Exception("AI 未返回有效内容，请重新尝试。")

            return response

        except Exception as e:

            error_message = str(e).upper()

            # 服务器繁忙或暂时不可用
            if (
                "503" in error_message
                or "UNAVAILABLE" in error_message
                or "429" in error_message
                or "RESOURCE_EXHAUSTED" in error_message
            ):

                if attempt < max_retries - 1:
                    wait_time = 2 * (attempt + 1)

                    time.sleep(wait_time)

                else:
                    raise Exception(
                        "Gemini 服务器暂时繁忙或请求次数达到限制。"
                        "请稍后再试。"
                    )

            else:
                raise e


# ==================== 侧边栏 ====================

with st.sidebar:

    st.markdown("## ⚡ 电力智能实验室")
    st.caption("POWER GRID AI ASSISTANT")

    st.divider()

    st.markdown("### 系统导航")
    st.markdown("💬  智能问答")
    st.markdown("📷  图片题目求解")

    st.divider()

    st.markdown("### 系统状态")
    st.success("API 密钥已加载")
    st.caption("当前模型：Gemini 3.5 Flash")
    st.caption("AI 服务：按需连接")

    st.divider()

    st.caption("配电网自动化技术")
    st.caption("课程设计项目 · 2026")


# ==================== 首页 ====================

st.markdown("""
<div class="hero">
    <h1>⚡ 配电网自动化技术智能体</h1>
    <p>专业知识问答 · 图片识别 · 智能分析 · 辅助学习</p>
    <p>POWER DISTRIBUTION AUTOMATION INTELLIGENT SYSTEM</p>
</div>
""", unsafe_allow_html=True)


# ==================== 信息卡片 ====================

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="info-card">
        <div class="info-title">系统功能</div>
        <div class="info-value">智能知识问答</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="info-card">
        <div class="info-title">图像处理</div>
        <div class="info-value">题目识别与求解</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="info-card">
        <div class="info-title">AI 服务</div>
        <div class="info-value">Gemini AI</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")


# ==================== 功能区域 ====================

tab1, tab2 = st.tabs([
    "💬  智能问答",
    "📷  图片题目求解"
])


# ==================== 智能问答 ====================

with tab1:

    st.markdown(
        '<div class="section-title">专业知识智能问答</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "请输入电力系统、配电网自动化或电气工程相关问题。"
    )

    question = st.text_area(
        "问题内容",
        placeholder="例如：什么是馈线自动化？它是如何实现故障隔离的？",
        height=130,
        label_visibility="collapsed"
    )

    if st.button("🚀 发送问题", key="ask_button"):

        if question.strip():

            with st.spinner("AI 正在分析问题，请稍候..."):

                try:

                    prompt = (
                        "你是一名专业的配电网自动化技术助手。"
                        "请使用简体中文回答。"
                        "要求专业、准确、容易理解。"
                        "注意区分光纤通信和光伏发电等专业术语。"
                        "涉及计算时，请列出公式、已知条件、计算步骤和结果。"
                        "如果问题存在条件不足，请明确说明。"
                        "\n\n用户问题："
                        + question
                    )

                    response = generate_with_retry(prompt)

                    st.markdown("### 📘 AI 分析结果")

                    st.markdown(
                        '<div class="answer-box">',
                        unsafe_allow_html=True
                    )

                    st.markdown(response.text)

                    st.markdown(
                        '</div>',
                        unsafe_allow_html=True
                    )

                except Exception as e:

                    st.error("AI 请求失败")

                    st.warning(str(e))

        else:
            st.warning("请先输入问题！")


# ==================== 图片题目求解 ====================

with tab2:

    st.markdown(
        '<div class="section-title">图片识别与智能解题</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "上传电气工程或配电网自动化相关题目图片，AI 将识别并分析。"
    )

    image = st.file_uploader(
        "上传题目图片",
        type=["png", "jpg", "jpeg"],
        help="支持 PNG、JPG、JPEG 格式",
        label_visibility="collapsed"
    )

    if image is not None:

        st.image(
            image,
            caption="题目预览",
            use_container_width=True
        )

        if st.button("🔍 开始识别与解答", key="image_button"):

            with st.spinner("AI 正在识别图片并分析题目..."):

                try:

                    image_part = types.Part.from_bytes(
                        data=image.getvalue(),
                        mime_type=image.type
                    )

                    prompt = (
                        "请识别图片中的题目，并使用简体中文解答。"
                        "先准确提取题目内容，再分析已知条件。"
                        "然后逐步说明解题思路、相关公式和计算过程。"
                        "涉及电路图时，请分析元件连接关系。"
                        "最后给出明确答案。"
                        "如果图片模糊或信息不足，请指出。"
                    )

                    response = generate_with_retry(
                        contents=[
                            prompt,
                            image_part
                        ]
                    )

                    st.markdown("### 📝 题目分析与解答")

                    st.markdown(
                        '<div class="answer-box">',
                        unsafe_allow_html=True
                    )

                    st.markdown(response.text)

                    st.markdown(
                        '</div>',
                        unsafe_allow_html=True
                    )

                except Exception as e:

                    st.error("图片识别失败")

                    st.warning(str(e))


# ==================== 页脚 ====================

st.markdown("""
<div class="footer">
    配电网自动化技术智能体 | POWER GRID AI ASSISTANT<br>
    课程设计项目 · 智能化电力技术学习平台
</div>
""", unsafe_allow_html=True)
