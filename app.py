import os
import time
import streamlit as st
from openai import OpenAI

# ===================== CẤU HÌNH TRANG =====================
st.set_page_config(
    page_title="Sáng tạo by DuyKhánh, QuốcHoàng & Bé HữuNhân",
    page_icon="💎",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ===================== CSS TÙY CHỈNH =====================
CUSTOM_CSS = """
<style>
/* ----------- Tổng thể ----------- */
html, body, [data-testid="stAppViewContainer"] {
  background: linear-gradient(180deg, #0b1b26 0%, #0f2638 100%);
  color: #e8f5ff;
  font-family: 'Segoe UI', sans-serif;
}

/* Hiệu ứng nền ánh sáng */
[data-testid="stAppViewContainer"]::before {
  content: "";
  position: fixed;
  inset: 0;
  background: radial-gradient(1000px 800px at 50% -10%, rgba(0,255,255,0.08), transparent 60%),
              radial-gradient(1000px 800px at 80% 120%, rgba(0,180,255,0.06), transparent 60%);
  z-index: -1;
}

/* ----------- Thanh trên (Topbar) ----------- */
.topbar {
  position: sticky;
  top: 0; z-index: 50;
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 18px;
  border-radius: 12px;
  background: linear-gradient(90deg, #052b40, #083e5a);
  box-shadow: 0 6px 20px rgba(0,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.08);
}
.brand {
  display:flex; align-items:center; gap:12px;
  font-weight:600; color:#aaf4ff; letter-spacing:0.4px;
}
.brand .logo {
  width:28px; height:28px; border-radius:6px;
  background: linear-gradient(135deg, #00eaff, #0066ff);
  box-shadow: 0 0 14px rgba(0,255,255,0.6);
}
.pill {
  font-size:13px; padding:6px 12px; border-radius:20px;
  background: rgba(255,255,255,0.07);
  color:#9fe8ff; border:1px solid rgba(255,255,255,0.12);
}

/* ----------- Khung chat ----------- */
.chat-wrapper {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px;
  padding: 16px;
  backdrop-filter: blur(8px);
}
.msg {
  display: inline-block; max-width: 92%;
  border-radius: 14px; padding: 12px 15px; margin: 6px 0;
  line-height: 1.55; font-size: 16px;
}
.msg.assistant {
  background: linear-gradient(180deg, #0f2b3a, #0a1922);
  color: #d9f3ff;
  border-left: 3px solid #00c2ff;
}
.msg.user {
  background: linear-gradient(180deg, #084f72, #063857);
  color: #eaf9ff;
  border-right: 3px solid #00d4ff;
}
.row {
  display:flex; width:100%;
}
.row.user { justify-content: flex-end; }
.row.assistant { justify-content: flex-start; }

/* ----------- Thẻ thông tin ----------- */
.card {
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(0,60,100,0.2);
  border-radius: 12px;
  padding: 14px;
  color: #ccefff;
  box-shadow: inset 0 0 15px rgba(0,200,255,0.05);
}

/* ----------- Input box ----------- */
[data-baseweb="textarea"] textarea, .stTextInput input {
  background: rgba(255,255,255,0.05) !important;
  color: #e8f9ff !important;
  border-radius: 10px !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
}

/* ----------- Button ----------- */
.stButton>button {
  background: linear-gradient(135deg, #00aaff, #0077ff);
  color: white; border: none;
  border-radius: 10px; padding: 8px 14px;
  box-shadow: 0 6px 20px rgba(0,255,255,0.25);
  font-weight: 500;
}
.stButton>button:hover { filter: brightness(1.1); }

/* ----------- Footer ----------- */
.footer {
  text-align:center;
  font-size:13px;
  color:#93dbff;
  margin-top: 18px;
  padding-top: 8px;
  border-top: 1px solid rgba(255,255,255,0.05);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ===================== THANH TRÊN =====================
st.markdown(
    """
    <div class="topbar">
        <div class="brand">
            <div class="logo"></div>
            <div><b>AI Assistant</b> • DuyKhánh, QuốcHoàng, Bé HữuNhân</div>
        </div>
        <div class="pill">Trạng thái: Online ✅</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ===================== KẾT NỐI API =====================
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ Thiếu OPENAI_API_KEY. Vào Settings → Secrets của Streamlit Cloud để thêm.")
    st.stop()
client = OpenAI(api_key=api_key)

# ===================== SIDEBAR =====================
with st.sidebar:
    st.header("⚙️ Cài đặt hệ thống")
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "o4-mini"], index=0)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
    max_tokens = st.slider("Max tokens", 64, 2048, 512, 64)
    st.markdown("---")
    if st.button("🧹 Làm mới hội thoại"):
        st.session_state.clear()
        st.rerun()
    st.caption("© 2025 – Sản phẩm bởi DuyKhánh, QuốcHoàng & Bé HữuNhân")

# ===================== BỘ NHỚ HỘI THOẠI =====================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Bạn là trợ lý chuyên nghiệp, giọng điệu lịch sự, trả lời bằng tiếng Việt, rõ ràng, dễ hiểu."}
    ]

# ===================== GIỚI THIỆU =====================
with st.expander("💎 Giới thiệu sản phẩm", expanded=True):
    st.markdown(
        """
        <div class="card">
        <b>AI Assistant</b> được phát triển bởi <b>DuyKhánh</b>, <b>QuốcHoàng</b> và <b>Bé HữuNhân</b> —
        nhằm mang đến trải nghiệm trò chuyện thông minh, chuyên nghiệp và tự nhiên nhất.
        </div>
        """,
        unsafe_allow_html=True,
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
        unsafe_allow_html=True,
    )
st.markdown('</div>', unsafe_allow_html=True)

# ===================== NHẬP VÀ TRẢ LỜI =====================
prompt = st.chat_input("Nhập câu hỏi hoặc yêu cầu của bạn...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
    st.markdown(f'<div class="row user"><div class="msg user">{prompt}</div></div>', unsafe_allow_html=True)

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
        st.caption(f"⏱️ Phản hồi sau {latency:.2f}s • Model: {model}")

        st.session_state.messages.append({"role": "assistant", "content": answer})

    except Exception as e:
        st.error(f"⚠️ Lỗi khi gọi OpenAI API: {e}")

# ===================== FOOTER =====================
st.markdown(
    """
    <div class="footer">
        © 2025 <b>DuyKhánh – QuốcHoàng – Bé HữuNhân</b> | Giao diện thiết kế bởi ChatGPT Studio |
        Mọi quyền được bảo lưu.
    </div>
    """,
    unsafe_allow_html=True,
)
