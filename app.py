import os
import streamlit as st
from openai import OpenAI

# -------------------- Cấu hình trang --------------------
st.set_page_config(page_title="Chat với OpenAI", page_icon="💬", layout="centered")
st.title("💬 Chat với OpenAI (sản phẩm của DuyKhánh, QuốcHoàng, Bé HưuNhân)")
st.caption("💡 Trợ lý AI thân thiện, trò chuyện bằng tiếng Việt • Model mặc định: gpt-4o-mini")

# -------------------- Lấy API key --------------------
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ Thiếu OPENAI_API_KEY. Vào **Settings → Secrets** của Streamlit Cloud để thêm.")
    st.stop()

client = OpenAI(api_key=api_key)

# -------------------- Sidebar --------------------
with st.sidebar:
    st.header("⚙️ Cài đặt")
    model = st.selectbox("Chọn model", ["gpt-4o-mini", "gpt-4o", "o4-mini"], index=0)
    temperature = st.slider("Nhiệt độ (Temperature)", 0.0, 1.0, 0.3, 0.1)
    max_tokens = st.slider("Số token tối đa", 64, 2048, 512, 64)
    st.caption("💬 Nhiệt độ thấp → trả lời ổn định hơn")

# -------------------- Bộ nhớ hội thoại --------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Bạn là trợ lý thân thiện, trả lời ngắn gọn, dễ hiểu, bằng tiếng Việt."}
    ]

# -------------------- Hiển thị hội thoại cũ --------------------
for m in st.session_state.messages:
    if m["role"] == "system":
        continue
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# -------------------- Ô nhập liệu --------------------
prompt = st.chat_input("Nhập câu hỏi hoặc tin nhắn của bạn...")

# -------------------- Gửi và nhận phản hồi --------------------
if prompt:
    # Lưu tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Gọi API OpenAI
            resp = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            answer = resp.choices[0].message.content
            st.markdown(answer)
            # Lưu câu trả lời
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"⚠️ Lỗi khi gọi OpenAI API: {e}")
