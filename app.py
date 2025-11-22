import streamlit as st
import base64
from openai import OpenAI

st.set_page_config(page_title="AI 深度笔记", page_icon="📖")

# === 侧边栏：用户设置 ===
with st.sidebar:
    st.title("⚙️ 个性化设置")
    # 为了方便测试，你可以先填在这里，部署时建议用 st.secrets
    api_key = st.secrets["SILICON_KEY"]
    
    st.markdown("---")
    # 这里对应你代码里的变量
    user_role = st.text_input("用户身份", value="学生")
    reading_goal = st.text_input("阅读目的", value="整理读书笔记，便于快速复习")
    style = st.selectbox("笔记风格", [
        "目标导向，结构化，逻辑清晰，简洁明了",
        "幽默风趣，通俗易懂",
        "深度学术，引用严谨",
        "金句摘录，适合发朋友圈"
    ])

# === 核心逻辑 ===
def get_ai_response(image_bytes, api_key, role, goal, style_pref):
    client = OpenAI(api_key=api_key, base_url="https://api.siliconflow.cn/v1")
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    # 【核心修改】植入你的 Prompt
    system_prompt = f"""
    你是一个读书笔记专家。
    用户身份：{role}。阅读目的：{goal}。
    请分析图片中的书籍内容，生成一份风格为【{style_pref}】的笔记。
    要求：不要单纯OCR，要结合用户身份进行深度解读。
    """

    try:
        response = client.chat.completions.create(
            model="Qwen/Qwen2-VL-72B-Instruct", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                    {"type": "text", "text": "请整理笔记"}
                ]}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"发生错误: {e}"

# === 主界面 ===
st.title("📖 AI 读书笔记助手")

uploaded_file = st.file_uploader("上传书页", type=["jpg", "png", "jpeg"])

if uploaded_file and api_key:
    st.image(uploaded_file, caption="预览", use_container_width=True)
    
    if st.button("✨ 生成个性化笔记", type="primary"):
        with st.spinner("AI 正在阅读并思考..."):
            bytes_data = uploaded_file.getvalue()
            # 传入所有参数
            note = get_ai_response(bytes_data, api_key, user_role, reading_goal, style)
            
            st.markdown("### 📝 笔记结果")
            st.markdown(note)
elif not api_key:
    st.warning("👈 请在侧边栏输入 API Key")
