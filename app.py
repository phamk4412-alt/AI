import os
import base64
from io import BytesIO
from PIL import Image
import streamlit as st
from openai import OpenAI

# -------------------- Cấu hình trang --------------------
st.set_page_config(page_title="Chat với OpenAI", page_icon="💬", layout="centered")
st.title("💬 Chat với OpenAI (DuyKhánh, QuốcHoàng, Bé HưuNhân)")
st.caption("Hỗ trợ văn bản + hình ảnh • Model mặc định: gpt-4o-mini")

# -------------------- API key --------------------
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ Thiếu OPENAI_API_KEY. Vào **Settings → Secrets** của Streamlit Cloud để thêm.")
    st.stop()

client = OpenAI(api_key=api_key)

# -------------------- Sidebar: cấu hình --------------------
with st.sidebar:
    st.header("⚙️ Cài đặt")
    model = st.selectbox("Chọn model", ["gpt-4o-mini", "gpt-4o", "o4-mini"], index=0)
    temperature = st.slider("Nhiệt độ (Temperature)", 0.0, 1.0, 0.3, 0.1)
    max_tokens = st.slider("Số token tối đa", 64, 2048, 512, 64)
    st.caption("💡 Nhiệt độ thấp → trả lời ổn định hơn")

# -------------------- Tiện ích ảnh --------------------
def _img_to_b64(img: Image.Image, fmt="PNG") -> str:
    buf = BytesIO()
    img.save(buf, format=fmt)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def _b64_to_img(b64: str) -> Image.Image:
    return Image.open(BytesIO(base64.b64decode(b64)))

# -------------------- Bộ nhớ hội thoại --------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Bạn là trợ lý thân thiện, trả lời ngắn gọn và dễ hiểu."}
    ]

# Hiển thị hội thoại trước đó
for m in st.session_state.messages:
    if m["role"] == "system":
        continue
    with st.chat_message(m["role"]):
        if isinstance(m["content"], dict):
            st.markdown(m["content"].get("text", ""))
            if m["content"].get("image_b64"):
                st.image(_b64_to_img(m["content"]["image_b64"]), caption="Ảnh đính kèm", use_column_width=True)
        else:
            st.markdown(m["content"])

# -------------------- Ô nhập liệu --------------------
st.markdown("### 💬 Nhập câu hỏi của bạn")
attach_cam = st.camera_input("📸 Chụp ảnh (tùy chọn)")
attach_file = st.file_uploader("📎 Hoặc tải ảnh từ máy", type=["png", "jpg", "jpeg"], key="upload")

attached_b64 = None
mime_type = None
if attach_cam:
    attached_b64 = base64.b64encode(attach_cam.getvalue()).decode("utf-8")
    mime_type = "image/png"
elif attach_file:
    attached_b64 = base64.b64encode(attach_file.getvalue()).decode("utf-8")
    mime_type = attach_file.type or "image/png"

prompt = st.chat_input("Nhập tin nhắn...")

# -------------------- Gửi câu hỏi --------------------
if prompt:
    # Lưu tin nhắn user
    if attached_b64:
        user_msg = {"text": prompt, "image_b64": attached_b64}
    else:
        user_msg = prompt

    st.session_state.messages.append({"role": "user", "content": user_msg})

    with st.chat_message("user"):
        st.markdown(prompt)
        if attached_b64:
            st.image(_b64_to_img(attached_b64), caption="Ảnh bạn gửi", use_column_width=True)

    with st.chat_message("assistant"):
        try:
            if attached_b64:
                # ===== Có ảnh → dùng Responses API =====
                content_blocks = [
                    {"type": "text", "text": prompt},
                    {"type": "input_image", "image_data": attached_b64, "mime_type": mime_type},
                ]
                resp = client.responses.create(
                    model=model,
                    input=[
                        {"role": "system", "content": [{"type": "text", "text": "Bạn là trợ lý AI thông minh, hiểu cả văn bản và hình ảnh."}]},
                        {"role": "user", "content": content_blocks},
                    ],
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
                answer = resp.output_text
            else:
                # ===== Không ảnh → Chat Completions API =====
                msgs = [{"role": "system", "content": "Bạn là trợ lý thân thiện, giúp người dùng bằng tiếng Việt dễ hiểu."}]
                for m in st.session_state.messages:
                    if m["role"] == "system":
                        continue
                    if isinstance(m["content"], dict):
                        txt = m["content"].get("text", "")
                    else:
                        txt = m["content"]
                    msgs.append({"role": m["role"], "content": txt})

                resp = client.chat.completions.create(
                    model=model,
                    messages=msgs,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                answer = resp.choices[0].message.content

            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

        except Exception as e:
            st.error(f"Lỗi khi gọi OpenAI API: {e}")
