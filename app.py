import os
import base64
from io import BytesIO
from PIL import Image
import streamlit as st
from openai import OpenAI

# -------------------- Cấu hình trang --------------------
st.set_page_config(page_title="Chat with OpenAI", page_icon="💬", layout="centered")

# -------------------- API key --------------------
api_key = st.secrets.get("OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("Chưa có OPENAI_API_KEY. Vào Settings → Secrets của Streamlit Cloud để thêm.")
    st.stop()
client = OpenAI(api_key=api_key)

# -------------------- Tiện ích ảnh --------------------
def _img_to_b64(img: Image.Image, fmt="PNG") -> str:
    buf = BytesIO(); img.save(buf, format=fmt)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def _file_to_b64(upload) -> str:
    if upload is None: return None
    return base64.b64encode(upload.getvalue()).decode("utf-8")

def _b64_to_img(b64: str) -> Image.Image:
    return Image.open(BytesIO(base64.b64decode(b64)))

# -------------------- State khởi tạo --------------------
if "profile" not in st.session_state:
    st.session_state.profile = {"name": "Bạn", "avatar_b64": None}

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system",
         "content": "Bạn là trợ lý hữu ích, trả lời ngắn gọn và đúng trọng tâm."}
    ]

# -------------------- Sidebar: Cài đặt + Hồ sơ --------------------
with st.sidebar:
    st.header("Cài đặt")
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "o4-mini"], index=0)
    temperature = st.slider("Nhiệt độ", 0.0, 1.0, 0.3, 0.1)
    max_tokens = st.slider("Max tokens (đáp án)", 64, 2048, 512, 64)
    st.markdown("---")

    st.subheader("🧑‍🎨 Hồ sơ")
    name = st.text_input("Tên hiển thị", value=st.session_state.profile["name"])

    c1, c2 = st.columns(2)
    with c1:
        up = st.file_uploader("Tải ảnh đại diện", type=["png", "jpg", "jpeg"])
    with c2:
        cam = st.camera_input("Chụp ảnh")

    avatar_img = None
    if cam is not None:
        avatar_img = Image.open(cam)
    elif up is not None:
        avatar_img = Image.open(up)

    st.session_state.profile["name"] = name
    if avatar_img is not None:
        st.session_state.profile["avatar_b64"] = _img_to_b64(avatar_img.convert("RGBA"))

    st.caption("Xem trước")
    pc1, pc2 = st.columns([1, 2])
    with pc1:
        if st.session_state.profile["avatar_b64"]:
            st.image(_b64_to_img(st.session_state.profile["avatar_b64"]), width=80, clamp=True)
        else:
            st.image("https://placehold.co/80x80?text=🙂", width=80, clamp=True)
    with pc2:
        st.markdown(f"**{st.session_state.profile['name']}**")

    if st.session_state.profile["avatar_b64"]:
        if st.button("Xóa ảnh đại diện"):
            st.session_state.profile["avatar_b64"] = None
            st.rerun()

# -------------------- Tiêu đề --------------------
header_l, header_r = st.columns([1, 6])
with header_l:
    if st.session_state.profile["avatar_b64"]:
        st.image(_b64_to_img(st.session_state.profile["avatar_b64"]), width=60)
    else:
        st.image("https://placehold.co/60x60?text=🙂", width=60)
with header_r:
    st.title("💬 Chat với OpenAI (sản phẩm của DuyKhánh, QuocHoàng, Bé HưuNhân)")
    st.caption(f"Model mặc định: gpt-4o-mini • Xin chào, **{st.session_state.profile['name']}** 👋")

# -------------------- Hiển thị lịch sử --------------------
for m in st.session_state.messages:
    if m["role"] == "system":
        continue
    with st.chat_message(m["role"]):
        # Nếu có trường 'image_b64' trong message (do người dùng gửi kèm ảnh), hiển thị ảnh
        if isinstance(m.get("content"), dict) and m["content"].get("text") is not None:
            st.markdown(m["content"]["text"])
            if m["content"].get("image_b64"):
                st.image(_b64_to_img(m["content"]["image_b64"]), caption="Ảnh đính kèm", use_column_width=True)
        else:
            st.markdown(m["content"])

# -------------------- Khu vực nhập + đính kèm ảnh --------------------
st.markdown("### Gửi câu hỏi")
attach_img_cam = st.camera_input("📸 Chụp ảnh đính kèm (tuỳ chọn)")
attach_img_file = st.file_uploader("Hoặc tải ảnh từ máy", type=["png", "jpg", "jpeg"], key="file_attach")

attached_b64 = None
mime_type = None
if attach_img_cam is not None:
    attached_b64 = base64.b64encode(attach_img_cam.getvalue()).decode("utf-8")
    mime_type = "image/png"
elif attach_img_file is not None:
    attached_b64 = base64.b64encode(attach_img_file.getvalue()).decode("utf-8")
    # đoán mime
    mime_type = "image/png" if attach_img_file.type in (None, "", "application/octet-stream") else attach_img_file.type

prompt = st.chat_input("Nhập câu hỏi của bạn…")

# -------------------- Gửi yêu cầu --------------------
if prompt:
    # Lưu bản ghi người dùng (kèm ảnh nếu có) để hiển thị lại
    if attached_b64:
        user_content = {"text": prompt, "image_b64": attached_b64}
        st.session_state.messages.append({"role": "user", "content": user_content})
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)
        if attached_b64:
            st.image(_b64_to_img(attached_b64), caption="Ảnh đính kèm", use_column_width=True)

    # --------- Tạo system prompt cá nhân hoá ---------
    system_prompt = f"""
    Bạn là trợ lý thân thiện và hữu ích. Khi phù hợp, xưng hô với người dùng bằng tên: {st.session_state.profile['name']}.
    Nếu có ảnh đính kèm, hãy mô tả nội dung và hỗ trợ theo yêu cầu. Trả lời ngắn gọn, đúng trọng tâm.
    """

    with st.chat_message("assistant"):
        try:
            if attached_b64:
                # ===== Dùng Responses API khi có ảnh =====
                content_blocks = [
                    {"type": "text", "text": f"{st.session_state.profile['name']}: {prompt}"},
                    {"type": "input_image", "image_data": attached_b64, "mime_type": mime_type or "image/png"},
                ]
                resp = client.responses.create(
                    model=model,  # gpt-4o-mini/4o hỗ trợ đa phương thức
                    input=[
                        {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
                        {"role": "user", "content": content_blocks},
                    ],
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
                answer = resp.output_text
            else:
                # ===== Không có ảnh → dùng Chat Completions truyền thống =====
                # Duy trì system prompt ở đầu
                msgs = [{"role": "system", "content": system_prompt}]
                # Chuyển các lịch sử cũ sang dạng text (bỏ phần ảnh nếu có)
                for m in st.session_state.messages:
                    if m["role"] == "system":
                        continue
                    if isinstance(m.get("content"), dict):
                        txt = m["content"].get("text", "")
                    else:
                        txt = m.get("content", "")
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
            # Fallback: nếu Responses API chưa khả dụng, thử ép về Chat Completions chỉ với text
            st.warning("Thử lại bằng chế độ văn bản do lỗi khi gửi ảnh.")
            try:
                msgs = [{"role": "system", "content": system_prompt}]
                msgs += [{"role": "user", "content": prompt}]
                resp = client.chat.completions.create(
                    model=model,
                    messages=msgs,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                answer = resp.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e2:
                st.error(f"Lỗi gọi OpenAI API: {e2}")
