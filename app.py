
import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, set_seed

st.set_page_config(page_title="AI Viết Văn Bản", page_icon="✍️", layout="centered")
st.title("✍️ AI Viết Văn Bản")

# 1) Chọn model: bắt đầu với distilgpt2 (nhẹ), có thể đổi sang model khác trên HF
MODEL_ID = st.sidebar.text_input("Model ID (Hugging Face)", value="distilgpt2",
                                 help="Ví dụ: distilgpt2. Bạn có thể thay bằng model khác như GPT-2 nhỏ.")
st.sidebar.caption("Mẹo: Đổi MODEL_ID rồi bấm Rerun để thử model khác.")

@st.cache_resource(show_spinner=False)
def load_generator(model_id: str):
    tok = AutoTokenizer.from_pretrained(model_id)
    mdl = AutoModelForCausalLM.from_pretrained(model_id)
    gen = pipeline("text-generation", model=mdl, tokenizer=tok, device_map="auto")
    return gen

try:
    generator = load_generator(MODEL_ID)
except Exception as e:
    st.error(f"Không tải được model `{MODEL_ID}` ({e}). Đang fallback về `distilgpt2`.")
    generator = load_generator("distilgpt2")

# 2) Tham số sinh văn bản
st.sidebar.subheader("⚙️ Tham số")
max_new_tokens = st.sidebar.slider("Độ dài thêm (tokens)", 16, 512, 120, 8)
temperature     = st.sidebar.slider("Temperature", 0.1, 2.0, 0.9, 0.1)
top_p           = st.sidebar.slider("Top-p (nucleus)", 0.1, 1.0, 0.95, 0.05)
top_k           = st.sidebar.slider("Top-k", 0, 200, 50, 5)
repetition_pen  = st.sidebar.slider("Repetition penalty", 0.8, 2.0, 1.1, 0.05)
seed            = st.sidebar.number_input("Seed (đặt cố định để tái lập)", 0, 10_000, 42)
num_return      = st.sidebar.slider("Số phương án", 1, 5, 1)

set_seed(seed)

# 3) Giao diện nhập prompt
st.markdown("### Nhập đề bài / mở đầu")
prompt = st.text_area("Gợi ý cho AI (tiếng Việt hoặc ngôn ngữ khác)",
                      height=160,
                      placeholder="Ví dụ: Hãy viết một đoạn mở đầu hấp dẫn cho bài blog về thói quen đọc sách buổi sáng...")

colA, colB = st.columns([1,1])
with colA:
    add_prefix = st.checkbox("Thêm tiền tố an toàn", value=True,
                             help="Giúp AI lịch sự, trung lập, không bịa quá đà.")
with colB:
    stop_at_dot = st.checkbox("Ưu tiên dừng sau dấu chấm", value=True)

safe_prefix = ("Viết một đoạn văn tự nhiên, lịch sự, không bịa đặt sự kiện. "
               "Nếu thiếu thông tin thì để chung chung. ")
if add_prefix and prompt.strip():
    full_prompt = safe_prefix + prompt.strip()
else:
    full_prompt = prompt.strip()

# 4) Nút sinh văn bản
if st.button("✨ Viết văn bản", use_container_width=True) and full_prompt:
    with st.spinner("Đang viết..."):
        out = generator(
            full_prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=None if top_k == 0 else top_k,
            num_return_sequences=num_return,
            do_sample=True,
            repetition_penalty=repetition_pen,
            pad_token_id=generator.tokenizer.eos_token_id,
            eos_token_id=None
        )

    st.markdown("## Kết quả")
    for i, o in enumerate(out, 1):
        text = o["generated_text"]
        # Cắt gọn nếu cần
        if stop_at_dot:
            # tìm dấu chấm đầu tiên sau phần prompt
            body = text[len(full_prompt):]
            cut = body.split(". ")
            if len(cut) > 1:
                text = full_prompt + ". ".join(cut[: max(1, min(5, len(cut)))])  # ghép vài câu đầu

        st.markdown(f"**Phương án {i}:**")
        st.write(text)
        st.divider()
else:
    st.info("Nhập gợi ý rồi bấm **✨ Viết văn bản** để bắt đầu.")

