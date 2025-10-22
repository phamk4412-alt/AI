import os
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Chat with OpenAI", page_icon="💬", layout="centered")

st.title("💬 Chat với OpenAI (sản phẩm của Khánh,Hoàng,Bé Nhân)")
st.caption("Model mặc định: gpt-4o-mini")

# Lấy API key từ st.secrets (khuyên dùng) hoặc biến môi trường
api_key = st.secrets.get("OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("Chưa có OPENAI_API_KEY. Vào Settings → Secrets của Streamlit Cloud để thêm.")
    st.stop()

client = OpenAI(api_key=api_key)

# Sidebar: tham số sinh
with st.sidebar:
    st.header("Cài đặt")
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "o4-mini"], index=0)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
    max_tokens = st.slider("Max tokens (đáp án)", 64, 2048, 512, 64)
    st.markdown("—")
    st.caption("Gợi ý: giữ temperature thấp để trả lời ổn định hơn.")

# Bộ nhớ hội thoại đơn giản
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Bạn là trợ lý hữu ích, trả lời ngắn gọn và đúng trọng tâm."}
    ]

for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

prompt = st.chat_input("Nhập câu hỏi của bạn...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            answer = resp.choices[0].message.content
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"Lỗi gọi OpenAI API: {e}")
