import os
import time
import streamlit as st
from openai import OpenAI

# ===================== CẤU HÌNH TRANG =====================
st.set_page_config(
    page_title="Enterprise AI Assistant",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ===================== CSS ENTERPRISE =====================
ENTERPRISE_CSS = """
<style>
/* Nền & font */
html, body, [data-testid="stAppViewContainer"] {
  background: #0b0f14;
}
[data-testid="stAppViewContainer"]::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background: radial-gradient(1000px 600px at 10% -10%, rgba(32,93,255,0.08), transparent 50%),
              radial-gradient(900px 500px at 110% 10%, rgba(0,194,255,0.06), transparent 50%);
}

/* Thanh top-bar */
.topbar {
  position: sticky;
  top: 0; z-index: 20;
  margin-bottom: 12px;
  border: 1px solid rgba(255,255,255,0.06);
  background: linear-gradient(180deg, rgba(18,24,33,0.9), rgba(10,14,20,0.9));
  backdrop-filter: blur(8px);
  border-radius: 14px;
  padding: 10px 16px;
  display: flex; align-items: center; justify-content: space-between;
}
.brand {
  display:flex; align-items:center; gap:12px;
  color: #e8eef8; font-weight: 600; letter-spacing: 0.3px;
}
.brand .logo {
  width: 28px; height: 28px; border-radius: 8px;
  background: linear-gradient(135deg, #205dff, #00c2ff);
  box-shadow: 0 6px 18px rgba(0,194,255,0.25);
}
.pill {
  font-size: 12px; padding: 6px 10px; border-radius: 999px;
  color:#b9c6d8; background:#0f1621; border:1px solid rgba(255,255,255,0.08);
}

/* Vùng hội thoại */
.chat-wrapper {
  border: 1px solid rgba(255,255,255,0.06);
  background: #0f141b;
  border-radius: 16px;
  padding: 12px;
}
.msg {
  display: inline-block; max-width: 92%;
  border-radius: 14px; padding: 12px 14px; margin: 6px 0;
  line-height: 1.55; font-size: 15.5px;
  border:1px solid rgba(255,255,255,0.06);
}
.msg.assistant {
  background: linear-gradient(180deg, #121a24, #0d141c);
  color: #e3ebf7;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
}
.msg.user {
  background: linear-gradient(180deg, #163166, #0c1f44);
  color: #e9f1ff;
  border-color: rgba(32,93,255,0.35);
  box-shadow: 0 6px 18px rgba(32,93,255,0.15);
}
.row {
  display:flex; width:100%;
}
.row.user { justify-content: flex-end; }
.row.assistant { justify-content: flex-start; }

/* Thẻ thông tin */
.card {
  border: 1px solid rgba(255,255,255,0.06);
  background: #0f141b;
  border-radius: 14px;
  padding: 14px;
  color: #b9c6d8;
}

/* Footer */
.footer {
  color:#6f7c8f; font-size:12.5px; text-align:center; margin-top: 14px;
}

/* Nút */
.stButton>button {
  background: linear-gradient(180deg, #205dff, #0f5bff);
  color: white; border: none;
  border-radius: 10px; padding: 8px 14px;
  box-shadow: 0 10px 22px rgba(32,93,255,0.25);
}
.stButton>button:hover { filter: brightness(1.05); }

/* Input */
[data-baseweb="textarea"] textarea, .stTextInput input {
  background: #0c1219 !important; color: #e6eefb !important;
  border-radius: 12px !important; border:1px solid rgba(255,255,255,0.08) !important;
}
</style>
"""
st.markdown(ENTERPRISE_CSS, unsafe_allow_html=True)

# ===================== NAVBAR =====================
col = st.container()
with col:
    st.markdown(
        f"""
        <div class="topbar">
          <div class="brand">
            <div class="logo"></div>
            <div>ALPHA CORPORATION • AI ASSISTANT</div>
          </div>
          <div class="pill">Status: Online</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ===================== LẤY API KEY =====================
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("Thiếu OPENAI_API_KEY. Vào **Settings → Secrets** của Streamlit Cloud để thêm.")
    st.stop()

client = OpenAI(api_key=api_key)

# ===================== SIDEBAR (TỐI GIẢN, DOANH NGHIỆP) =====================
with st.sidebar:
    st.markdown("#### Control Panel")
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "o4-mini"], index=0)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
    max_tokens = st.slider("Max tokens", 64, 2048, 512, 64)
    st.markdown("---")
    if st.button("↺ New chat"):
        st.session_state.clear()
        st.rerun()
    st.caption("© Alpha Corp — Internal Use Only")

# ===================== BỘ NHỚ HỘI THOẠI =====================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system",
         "content": "Bạn là trợ lý doanh nghiệp: ngắn gọn, chính xác, giọng điệu chuyên nghiệp, tiếng Việt."}
    ]

# ===================== HỘP THÔNG TIN (CARD) =====================
with st.expander("Giới thiệu sản phẩm", expanded=True):
    st.markdown(
        """
        <div class="card">
        <strong>Alpha Corporation AI Assistant</strong> giúp tăng tốc tra cứu, tóm tắt & soạn thảo.
        Tối ưu cho bảo mật và độ tin cậy. Không lưu ảnh, không dùng micro.
        </div>
        """, unsafe_allow_html=True
    )

# ===================== HIỂN THỊ HỘI THOẠI =====================
st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
for m in st.session_state.messages:
    if m["role"] == "system":
        continue
    role = m["role"]
    css_role = "assistant" if role == "assistant" else "user"
    st.markdown(
        f"""
        <div class="row {css_role}">
          <div class="msg {css_role}">{m["content"]}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
st.markdown('</div>', unsafe_allow_html=True)

# ===================== Ô NHẬP & GỬI =====================
prompt = st.chat_input("Nhập câu hỏi của bạn…")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Render ngay tin nhắn người dùng theo style tùy biến (để đồng bộ UX)
    st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
    st.markdown(f'<div class="row user"><div class="msg user">{prompt}</div></div>', unsafe_allow_html=True)

    # Gọi API
    try:
        start = time.time()
        resp = client.chat.completions.create(
            model=model,
            messages=st.session_state.messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        answer = resp.choices[0].message.content
        latency = time.time() - start

        st.markdown(f'<div class="row assistant"><div class="msg assistant">{answer}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Thêm “thẻ hiệu năng” nhỏ
        st.caption(f"⏱️ Phản hồi {latency:.2f}s • Model: {model}")

        st.session_state.messages.append({"role": "assistant", "content": answer})

    except Exception as e:
        st.markdown('</div>', unsafe_allow_html=True)
        st.error(f"Không thể gọi OpenAI API: {e}")

# ===================== FOOTER =====================
st.markdown(
    """
    <div class="footer">
      © 2025 Alpha Corporation. All rights reserved. | Confidential & Proprietary.
    </div>
    """,
    unsafe_allow_html=True
)
