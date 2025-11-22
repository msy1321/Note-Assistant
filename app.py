import streamlit as st
import base64
from openai import OpenAI

# 从 Streamlit 的云端配置里读取 Key，这样安全
# 如果本地运行报错，可以先暂时写死，上传前改回来
api_key = st.secrets["SILICON_KEY"] 
base_url = "https://api.siliconflow.cn/v1"

st.title("📚 云端读书笔记")

uploaded_file = st.file_uploader("上传书页", type=["jpg", "png", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="预览", use_container_width=True)
    
    if st.button("生成笔记"):
        with st.spinner("AI 正在阅读..."):
            client = OpenAI(api_key=api_key, base_url=base_url)
            
            # 处理图片
            bytes_data = uploaded_file.getvalue()
            base64_img = base64.b64encode(bytes_data).decode('utf-8')
            
            try:
                response = client.chat.completions.create(
                    model="Qwen/Qwen2-VL-72B-Instruct", # 记得改成你测试成功的 7B 或 72B
                    messages=[
                        {"role": "user", "content": [
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}},
                            {"type": "text", "text": "请整理这份读书笔记，风格要结构化。"}
                        ]}
                    ]
                )
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"报错了: {e}")