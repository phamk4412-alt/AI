import os
import time
import streamlit as st
from openai import OpenAI

# ===================== CẤU HÌNH TRANG =====================
st.set_page_config(
    page_title="AI Assistant by DuyKhánh, QuốcHoàng & Bé HữuNhân",
    page_icon="💎",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ===================== SIDEBAR: CHỌN GIAO DIỆN + MODEL =====================
with st.sidebar:
    st.header("⚙️ Cài đặt hệ thống")
    theme_mode = st.radio("🎨 Chế độ hiển thị", ["🌙 Tối", "🌞 Sáng"], horizontal=True)
    model = st.selectbox("🤖 Model", ["gpt-4o-mini", "gpt-4o", "o4-mini"], index=0)
    temperature = st.slider("🔥 Temperature", 0.0, 1.0, 0.3, 0.1)
    max_tokens = st.slider("🧠 Max tokens", 64, 2048, 512, 64)
    st.markdown("---")
    if st.button("🧹 Làm mới hội thoại"):
        st.session_state.clear()
        st.rerun()
    st.caption("© 2025 – Sản phẩm bởi DuyKhánh, QuốcHoàng & Bé HữuNhân")

# ===================== MÀU SẮC THEO CHỦ ĐỀ =====================
if theme_mode == "🌙 Tối":
    BACKGROUND = "#0b1b26"
    SECOND_BG = "#0f2638"
    TEXT = "#e8f5ff"
    ACCENT = "#00c2ff"
    CARD_BG = "rgba(0,60,100,0.2)"
else:
    BACKGROUND = "#f9fcff"
    SECOND_BG = "#dceeff"
    TEXT = "#0a2233"
    ACCENT = "#0077cc"
    CARD_BG = "#ffffff"

# ===================== CSS ĐỘNG =====================
CUSTOM_CSS = f"""
<style>
html, body, [data-testid="stAppViewContainer"] {{
  background: linear-gradient(180deg, {BACKGROUND}, {SECOND_BG});
  color: {TEXT};
  font-family: 'Segoe UI', sans-serif;
}}

.topbar {{
  position: sticky; top: 0; z-index: 50;
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 18px; border-radius: 12px;
  background: linear-gradient(90deg, {ACCENT}22, {ACCENT}11);
  box-shadow: 0 4px 14px {ACCENT}33;
  border: 1px solid {ACCENT}33;
}}
.brand {{
  display:flex; align-items:center; gap:12px;
  font-weight:600; color:{ACCENT};
}}
.brand .logo {{
  width:28px; height:28px; border-radius:6px;
  background: linear-gradient(135deg, {ACCENT}, #0066ff);
  box-shadow: 0 0 14px {ACCENT}66;
}}
.pill {{
  font-size:13px; padding:6px 12px; border-radius:20px;
  background: {ACCENT}11;
  color:{TEXT}; border:1px solid {ACCENT}33;
}}

.chat-wrapper {{
  background: {CARD_BG};
  border: 1px solid {ACCENT}22;
  border-radius: 16px;
  padding: 16px;
}}
.msg {{
  display: inline-block; max-width: 92%;
  border-radius: 14px; padding: 12px 15px; margin: 6px 0;
  line-height: 1.55; font-size: 16px;
}}
.msg.assistant {{
  background: linear-gradient(180deg, {ACCENT}22, {ACCENT}11);
  color: {TEXT};
  border-left: 3px solid {ACCENT};
}}
.msg.user {{
  background: linear-gradient(180deg, {ACCENT}44, {ACCENT}33);
  color: {TEXT};
  border-right: 3px solid {ACCENT};
}}
.row {{ display:flex; width:100%; }}
.row.user {{ justify-content: flex-end; }}
.row.assistant {{ justify-content: flex-start; }}

.card {{
  border: 1px solid {ACCENT}33;
  background: {CARD_BG};
  border-radius: 12px;
  padding: 14px;
  color: {TEXT};
  box-shadow: inset 0 0 15px {ACCENT}15;
}}

[data-baseweb="textarea"] textarea, .stTextInput input {{
  background: {ACCENT}08 !important;
  color: {TEXT} !important;
  border-radius: 10px !important;
  border: 1px solid {ACCENT}33 !important;
}}

.stButton>button {{
  background: linear-gradient(135deg, {ACCENT}, #0077ff);
  color: white; border: none;
  border-radius: 10px; padding: 8px 14px;
  box-shadow: 0 6px 20px {ACCENT}33;
  font-weight: 500;
}}
.stButton>button:hover {{ filter: brightness(1.1); }}

.footer {{
  text-align:center;
  font-size:13px;
  color:{TEXT}AA;
  margin-top: 18px;
  padding-top: 8px;
  border-top: 1px solid {ACCENT}22;
}}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ===================== THANH TRÊN =====================
st.markdown(
    f"""
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

# ===================== API KEY =====================
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ Thiếu OPENAI_API_KEY. Vào Settings → Secrets của Streamlit Cloud để thêm.")
    st.stop()
client = OpenAI(api_key=api_key)

# ===================== BỘ NHỚ HỘI THOẠI =====================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system",
         "content": "Bạn là trợ lý chuyên nghiệp, trả lời bằng tiếng Việt, giọng điệu lịch sự, dễ hiểu."}
    ]

# ===================== GIỚI THIỆU =====================
with st.expander("💎 Giới thiệu sản phẩm", expanded=True):
    st.markdown(
        f"""
        <div class="card">
        <b>AI Assistant</b> được phát triển bởi <b>DuyKhánh</b>, <b>QuốcHoàng</b> và <b>Bé HữuNhân</b> —
        mang đến trải nghiệm hội thoại AI thân thiện, thông minh và dễ sử dụng.
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

# ===================== NHẬP VÀ PHẢN HỒI =====================
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
    f"""
    <div class="footer">
        © 2025 <b>DuyKhánh – QuốcHoàng – Bé HữuNhân</b> | 
        Giao diện { 'Tối' if theme_mode == '🌙 Tối' else 'Sáng' } | 
        All rights reserved.
    </div>
    """,
    unsafe_allow_html=True,
)
