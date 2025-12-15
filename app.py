import streamlit as st
from rembg import remove, new_session
from PIL import Image, ImageOps
from io import BytesIO
import zipfile

st.set_page_config(page_title="专业批量抠图工具", page_icon="🖼️", layout="centered")

st.title("🖼️ 专业在线批量产品抠图工具")
st.caption("多模型选择 + Alpha Matting 边缘优化 + 可输出白底图")

# ================= 多模型选择 =================
model_options = {
    "isnet-general-use": "🌟 推荐：产品/物体（边缘最自然）",
    "u2net": "📦 默认通用模型",
    "u2netp": "⚡ 轻量快速",
    "u2net_human_seg": "👤 人物专用（头发丝超准）",
    "isnet-anime": "🎨 动漫风格"
}

selected_model = st.selectbox(
    "选择 AI 模型",
    options=list(model_options.keys()),
    format_func=lambda x: model_options[x],
    index=0
)

# ================= 高级优化选项 =================
with st.expander("🔧 高级优化设置（推荐开启）"):
    alpha_matting = st.checkbox("开启 Alpha Matting（精细边缘处理，强烈推荐产品图）", value=True)
    if alpha_matting:
        erode_size = st.slider("边缘腐蚀大小（去黑边/毛边）", 5, 20, 10)
        fg_threshold = st.slider("前景阈值（保留更多细节）", 200, 255, 240)
        bg_threshold = st.slider("背景阈值（去除更多背景）", 0, 50, 10)
    
    white_bg = st.checkbox("同时输出白底版（电商产品图专用）", value=True)

# ================= 上传图片 =================
uploaded_files = st.file_uploader(
    "上传图片（支持批量）",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("🚀 开始批量抠图", type="primary", use_container_width=True):
        with st.spinner(f"加载 {model_options[selected_model]} 模型..."):
            session = new_session(selected_model)

        progress_bar = st.progress(0)
        status_text = st.empty()
        
        output_zip = BytesIO()
        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for idx, uploaded_file in enumerate(uploaded_files):
                progress = (idx + 1) / len(uploaded_files)
                progress_bar.progress(progress)
                status_text.text(f"处理中：{uploaded_file.name} ({idx + 1}/{len(uploaded_files)})")
                
                try:
                    input_image = Image.open(uploaded_file).convert("RGBA")
                    
                    # 核心抠图（带优化参数）
                    output_image = remove(
                        input_image,
                        session=session,
                        alpha_matting=alpha_matting,
                        alpha_matting_foreground_threshold=fg_threshold if alpha_matting else 240,
                        alpha_matting_background_threshold=bg_threshold if alpha_matting else 10,
                        alpha_matting_erode_size=erode_size if alpha_matting else 10
                    )
                    
                    # 保存透明版
                    transparent_io = BytesIO()
                    output_image.save(transparent_io, format="PNG")
                    zip_file.writestr(uploaded_file.name.rsplit(".", 1)[0] + "_透明.png", transparent_io.getvalue())
                    
                    # 可选白底版
                    if white_bg:
                        white_bg_img = Image.new("RGB", output_image.size, (255, 255, 255))
                        white_bg_img.paste(output_image, mask=output_image.split()[-1])
                        white_io = BytesIO()
                        white_bg_img.save(white_io, format="JPEG", quality=95)
                        zip_file.writestr(uploaded_file.name.rsplit(".", 1)[0] + "_白底.jpg", white_io.getvalue())
                
                except Exception as e:
                    st.error(f"{uploaded_file.name} 处理失败：{e}")
        
        progress_bar.empty()
        status_text.empty()
        
        st.success(f"🎉 完成！处理 {len(uploaded_files)} 张图片")
        output_zip.seek(0)
        
        st.download_button(
            label="📦 下载全部结果（ZIP 包，含透明+白底）",
            data=output_zip,
            file_name="专业抠图结果.zip",
            mime="application/zip",
            use_container_width=True
        )
else:
    st.info("👆 请上传图片并调整设置开始抠图")

st.markdown("---")
st.caption("基于 rembg 多模型 + Alpha Matting 优化 · 完全免费 · 隐私保护")
