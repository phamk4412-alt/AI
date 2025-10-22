import os
import streamlit as st
from openai import OpenAI
from pathlib import Path

# ============ CẤU HÌNH CƠ BẢN ============
st.set_page_config(page_title="Chat với OpenAI", page_icon="💬", layout="centered")

# Lấy API key (ưu tiên st.secrets)
api_key = st.secrets.get("OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("Chưa có OPENAI_API_KEY. Vào Settings → Secrets của Streamlit Cloud để thêm.")
    st.stop()

client = OpenAI(api_key=api_key)

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("## Cài đặt")

    # Giao diện
    theme_mode = st.radio("Giao diện", ["Sáng", "Tối", "Tùy chỉnh"], index=0)

    # Tham số Chat
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "o4-mini"], index=0)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
    max_tokens = st.slider("Max tokens (đáp án)", 64, 4096, 512, 64)
    st.caption("Gợi ý: giữ temperature thấp để trả lời ổn định hơn.")

    st.divider()
    st.markdown("#### Tùy chỉnh giao diện (Custom)")
    # Các control chỉ bật khi chọn Tùy chỉnh
    disabled = (theme_mode != "Tùy chỉnh")
    bg = st.color_picker("Nền (bg)", "#0B1220", disabled=disabled)
    surface = st.color_picker("Bề mặt (card)", "#131B2E", disabled=disabled)
    primary = st.color_picker("Nhấn (primary)", "#3B82F6", disabled=disabled)
    text = st.color_picker("Chữ (text)", "#E5E7EB", disabled=disabled)
    subtle = st.color_picker("Chữ phụ (muted)", "#9CA3AF", disabled=disabled)
    radius = st.slider("Bo góc (px)", 8, 28, 18, disabled=disabled)
    shadow = st.selectbox("Độ đổ bóng", ["nhẹ", "vừa", "đậm"], index=1, disabled=disabled)
    font = st.selectbox("Font chữ", ["Inter, system-ui", "Poppins, system-ui", "Roboto, system-ui"], index=0, disabled=disabled)

# ============ TẠO CSS THEO THEME ============
def build_css():
    if theme_mode == "Sáng":
        palette = {
            "bg": "#F7F8FA",
            "surface": "#FFFFFF",
            "primary": "#0EA5E9",
            "text": "#0F172A",
            "muted": "#475569",
            "radius": 14,
            "shadow": "0 8px 28px rgba(2,8,23,.06)",
            "font": "Inter, system-ui",
        }
    elif theme_mode == "Tối":
        palette = {
            "bg": "#0B1220",
            "surface": "#121826",
            "primary": "#3B82F6",
            "text": "#E5E7EB",
            "muted": "#9CA3AF",
            "radius": 16,
            "shadow": "0 10px 36px rgba(0,0,0,.45)",
            "font": "Inter, system-ui",
        }
    else:
        shadow_map = {
            "nhẹ": "0 6px 18px rgba(0,0,0,.12)",
            "vừa": "0 10px 30px rgba(0,0,0,.20)",
            "đậm": "0 16px 48px rgba(0,0,0,.32)",
        }
        palette = {
            "bg": bg,
            "surface": surface,
            "primary": primary,
            "text": text,
            "muted": subtle,
            "radius": radius,
            "shadow": shadow_map[shadow],
            "font": font,
        }

    css = f"""
    <style>
      :root {{
        --bg: {palette['bg']};
        --surface: {palette['surface']};
        --primary: {palette['primary']};
        --text: {palette['text']};
        --muted: {palette['muted']};
        --radius: {palette['radius']}px;
        --shadow: {palette['shadow']};
        --font: {palette['font']};
      }}
      html, body, [data-testid="stAppViewContainer"] {{
        background: var(--bg) !important;
        color: var(--text);
        font-family: var(--font);
      }}
      /* Topbar */
      .brand-wrap {{
        position: sticky; top: 0; z-index: 50;
        background: linear-gradient(180deg, rgba(0,0,0,.08), rgba(0,0,0,0));
        padding: 12px 0 4px;
      }}
      .brand {{
        display:flex; align-items:center; gap:12px; padding:12px 16px;
        background: var(--surface); border-radius: var(--radius);
        box-shadow: var(--shadow);
        border: 1px solid rgba(148,163,184,.12);
      }}
      .brand .title {{
        font-weight: 700; letter-spacing: .3px; font-size: 18px;
      }}
      .brand .subtitle {{ color: var(--muted); font-size: 12px; }}

      /* Cards + chat bubbles */
      .card {{
        background: var(--surface); border-radius: var(--radius);
        box-shadow: var(--shadow); padding: 18px; border: 1px solid rgba(148,163,184,.12);
      }}
      .bubble-user {{
        background: rgba(59,130,246,.12); border: 1px solid rgba(59,130,246,.3);
      }}
      .bubble-ai {{
        background: rgba(148,163,184,.08); border: 1px solid rgba(148,163,184,.18);
      }}
      /* Accent */
      .accent {{ color: var(--primary); }}
      a, .st-emotion-cache-16idsys p a {{ color: var(--primary) !important; }}
      .credit {{
        color: var(--muted); font-size: 12px; text-align:center; margin-top: 18px;
      }}
      /* Input box */
      [data-testid="stChatInput"] > div {{
        border-radius: var(--radius) !important; border: 1px solid rgba(148,163,184,.18);
        box-shadow: var(--shadow);
      }}
    </style>
    """
    return css

st.markdown(build_css(), unsafe_allow_html=True)

# ============ BRAND BAR (logo nếu có) ============
logo_path = Path("assets/logo.png")
logo_html = ""
if logo_path.exists():
    # hiển thị logo nếu repo có assets/logo.png
    logo_html = f'<img src="assets/logo.png" width="28" height="28" style="border-radius:8px;">'

st.markdown(
    f"""
    <div class="brand-wrap">
      <div class="brand">
        {logo_html}
        <div>
          <div class="title">💬 Chat với OpenAI</div>
          <div class="subtitle">Giao diện cấp doanh nghiệp — do <span class="accent">DuyKhanh, QuốcHoàng, béHữuNhân</span> phát triển</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============ BỘ NHỚ HỘI THOẠI ============
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Bạn là trợ lý hữu ích, trả lời ngắn gọn và đúng trọng tâm."}
    ]

# ============ LỊCH SỬ ============
for m in st.session_state.messages:
    if m["role"] == "user":
        with st.chat_message("user"):
            st.markdown(f'<div class="card bubble-user">{m["content"]}</div>', unsafe_allow_html=True)
    elif m["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(f'<div class="card bubble-ai">{m["content"]}</div>', unsafe_allow_html=True)

# ============ Ô CHAT ============
prompt = st.chat_input("Nhập câu hỏi của bạn…")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f'<div class="card bubble-user">{prompt}</div>', unsafe_allow_html=True)

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=st.session_state.messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        answer = resp.choices[0].message.content
    except Exception as e:
        answer = f"Xin lỗi, có lỗi khi gọi OpenAI API: `{e}`"

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(f'<div class="card bubble-ai">{answer}</div>', unsafe_allow_html=True)

# ============ FOOTER ============
st.markdown(
    """
    <div class="credit">
      © 2025 — Sản phẩm của <strong>DuyKhanh</strong>, <strong>QuốcHoàng</strong>, <strong>béHữuNhân</strong>.  
      Yêu cầu tính năng mới? Nhắn ngay trong hộp chat này.
    </div>
    """,
    unsafe_allow_html=True,
)
