
import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ==========================================
# 1. 基本配置
# ==========================================

load_dotenv()

st.set_page_config(
    page_title="配电网自动化技术智能体",
    page_icon="⚡",
    layout="wide"
)

# 修改 Gemini 模型只需要修改这一行
MODEL_NAME = "gemini-3.1-flash-lite"

# ==========================================
# 2. API 配置
# ==========================================

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("未找到 Gemini API Key，请检查 Streamlit Secrets。")
    st.stop()

client = genai.Client(api_key=API_KEY)

# ==========================================
# 3. 页面样式
# ==========================================

st.markdown("""
<style>

/* 页面整体 */
.stApp {
    background-color: #F4F7FB;
    color: #172B4D;
}

/* 主内容 */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* 侧边栏 */
section[data-testid="stSidebar"] {
    background-color: #E8F0FA;
    border-right: 1px solid #C8D7EA;
}

section[data-testid="stSidebar"] * {
    color: #172B4D !important;
}

/* 主标题 */
.main-title {
    text-align: center;
    color: #124A8C;
    font-size: 32px;
    font-weight: 800;
    margin-bottom: 8px;
}

.sub-title {
    text-align: center;
    color: #405875;
    font-size: 15px;
    margin-bottom: 28px;
}

/* 卡片 */
.answer-card {
    background-color: #FFFFFF;
    border: 1px solid #C9D8EA;
    border-radius: 12px;
    padding: 22px;
    min-height: 220px;
    box-shadow: 0 2px 8px rgba(20, 55, 90, 0.06);
}

/* Tiêu đề trong card */
.answer-heading {
    font-size: 21px;
    font-weight: 800;
    color: #1555A0;
    border-bottom: 2px solid #D9E7F7;
    padding-bottom: 12px;
    margin-bottom: 16px;
}

/* Nội dung */
.answer-content {
    color: #172B4D;
    font-size: 16px;
    line-height: 1.85;
}

/* Tất cả nội dung Markdown */
.stMarkdown,
.stMarkdown p,
.stMarkdown li,
.stMarkdown span {
    color: #172B4D;
}

/* Tiêu đề */
h1, h2, h3 {
    color: #124A8C !important;
    font-weight: 750 !important;
}

/* Input */
.stTextArea textarea {
    background-color: #FFFFFF !important;
    color: #172B4D !important;
    border: 1px solid #A9BED8 !important;
    border-radius: 9px !important;
    font-size: 16px !important;
}

.stTextArea textarea::placeholder {
    color: #64748B !important;
}

/* Button */
.stButton button {
    background-color: #1765B5;
    color: #FFFFFF !important;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 700;
    padding: 10px 20px;
}

.stButton button:hover {
    background-color: #104B8A;
    color: #FFFFFF !important;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    color: #334B68 !important;
    font-size: 16px;
    font-weight: 700;
}

.stTabs [aria-selected="true"] {
    color: #1555A0 !important;
}

/* Footer */
.footer {
    text-align: center;
    color: #526780;
    font-size: 13px;
    padding: 20px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. 侧边栏
# ==========================================

with st.sidebar:

    st.markdown("## ⚡ 配电网 AI 助手")

    st.divider()

    st.markdown("### 系统信息")

    st.write("**AI 模型：**")
    st.code(MODEL_NAME)

    st.write("**系统版本：** 2.0")

    st.divider()

    st.markdown("### 功能介绍")

    st.markdown("""
    - 💬 智能问答
    - 📷 图片题目求解
    - 🇨🇳 中文知识讲解
    - 🇻🇳 越南语翻译
    """)

    st.divider()

    st.caption("配电网自动化技术智能体")

# ==========================================
# 5. 页面标题
# ==========================================

st.markdown(
    '<div class="main-title">⚡ 配电网自动化技术智能体</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '专业知识问答 · 图片识别 · 双语解答'
    '</div>',
    unsafe_allow_html=True
)

# ==========================================
# 6. AI 请求函数
# ==========================================

def generate_answer(contents):

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents
        )

        if not response or not response.text:
            raise Exception("AI 未返回有效内容。")

        return response.text

    except Exception as e:

        error = str(e)
        upper_error = error.upper()

        if "429" in upper_error or "RESOURCE_EXHAUSTED" in upper_error:
            raise Exception(
                "Gemini API 请求额度不足或达到速率限制。"
                "请检查当前模型的配额和重置时间。\n\n"
                + error
            )

        if "404" in upper_error or "NOT_FOUND" in upper_error:
            raise Exception(
                "当前 Gemini 模型不可用或没有访问权限。"
                "请检查模型名称。\n\n"
                + error
            )

        raise Exception("Gemini API 请求失败：\n" + error)

# ==========================================
# 7. 生成双语提示词
# ==========================================

def build_prompt(question):

    return f"""
你是一名专业的配电网自动化技术专家，
同时也是一名大学电气工程教师。

请回答以下问题：

{question}

回答要求：

一、中文部分：
1. 使用规范、自然的简体中文。
2. 先解释基本概念，再讲解工作原理。
3. 涉及计算时，写出公式、代入过程和结果。
4. 涉及电路时，解释电流、电压和能量的物理意义。
5. 内容准确、清楚，适合大学生学习。

二、越南语部分：
1. 将上面的中文答案完整翻译成越南语。
2. 保持原意、公式、数据和步骤一致。
3. 使用自然、容易理解的越南语。

必须严格使用以下格式：

【中文回答】
在这里写完整的中文答案。

【越南语翻译】
在这里写完整的越南语翻译。
"""

# ==========================================
# 8. 显示双语答案
# ==========================================

def display_answer(answer):

    if "【中文回答】" not in answer or "【越南语翻译】" not in answer:

        st.warning("AI 返回格式不完整，以下显示原始回答。")
        st.markdown(answer)
        return

    parts = answer.split("【越南语翻译】", 1)

    chinese = parts[0].split("【中文回答】", 1)[1].strip()
    vietnamese = parts[1].strip()

    # 两个独立的答案区域
    tab_cn, tab_vi = st.tabs([
        "🇨🇳 中文回答",
        "🇻🇳 越南语翻译"
    ])

    with tab_cn:

        st.markdown(
            '<div class="answer-card">'
            '<div class="answer-heading">🇨🇳 中文回答</div>'
            '<div class="answer-content">',
            unsafe_allow_html=True
        )

        st.markdown(chinese)

        st.markdown("</div></div>", unsafe_allow_html=True)

    with tab_vi:

        st.markdown(
            '<div class="answer-card">'
            '<div class="answer-heading">🇻🇳 越南语翻译</div>'
            '<div class="answer-content">',
            unsafe_allow_html=True
        )

        st.markdown(vietnamese)

        st.markdown("</div></div>", unsafe_allow_html=True)

# ==========================================
# 9. 功能选项卡
# ==========================================

tab1, tab2 = st.tabs([
    "💬 智能问答",
    "📷 图片题目求解"
])

# ==========================================
# 10. 智能问答
# ==========================================

with tab1:

    st.subheader("💬 智能问答")

    st.write(
        "请输入与配电网自动化、电力系统、电气工程相关的问题。"
    )

    question = st.text_area(
        "问题内容",
        placeholder="例如：什么是配电网自动化？它有哪些主要功能？",
        height=150,
        key="question_input"
    )

    if st.button("🚀 提交问题", key="submit_question"):

        if not question.strip():

            st.warning("请先输入问题。")

        else:

            with st.spinner("AI 正在分析问题，请稍候..."):

                try:

                    prompt = build_prompt(question)

                    answer = generate_answer(prompt)

                    st.success("回答完成！")

                    display_answer(answer)

                except Exception as e:

                    st.error("请求失败")
                    st.code(str(e))

# ==========================================
# 11. 图片题目求解
# ==========================================

with tab2:

    st.subheader("📷 图片题目求解")

    st.write(
        "上传电气工程或配电网自动化相关题目图片，"
        "AI 将识别题目并给出详细解答。"
    )

    uploaded_file = st.file_uploader(
        "上传题目图片",
        type=["png", "jpg", "jpeg"],
        help="支持 PNG、JPG、JPEG 格式"
    )

    if uploaded_file is not None:

        st.image(
            uploaded_file,
            caption="已上传的题目图片",
            use_container_width=True
        )

        if st.button("🔍 识别并解答", key="solve_image"):

            with st.spinner("AI 正在识别图片并分析题目..."):

                try:

                    image_bytes = uploaded_file.getvalue()

                    image_part = types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=uploaded_file.type
                    )

                    image_prompt = """
你是一名专业的电气工程和配电网自动化技术教师。

请认真识别图片中的题目，并完成以下任务：

1. 提取图片中的完整题目。
2. 分析题目所考查的知识点。
3. 给出详细的解题过程。
4. 涉及计算时，写出公式、代入步骤和最终结果。
5. 涉及电路图时，分析电路结构和工作原理。
6. 如果图片不清晰或信息不足，请明确指出，不要猜测。

请分别使用简体中文和越南语回答。

格式必须为：

【中文回答】
题目识别、知识点分析、详细解题过程和答案。

【越南语翻译】
以上全部内容的完整越南语翻译。
"""

                    answer = generate_answer([
                        image_prompt,
                        image_part
                    ])

                    st.success("图片识别与解答完成！")

                    display_answer(answer)

                except Exception as e:

                    st.error("图片识别或解答失败")
                    st.code(str(e))

# ==========================================
# 12. 页面底部
# ==========================================

st.markdown("---")

st.markdown(
    """
    <div class="footer">
        ⚡ 配电网自动化技术智能体<br>
        Powered by Gemini API
    </div>
    """,
    unsafe_allow_html=True
)
