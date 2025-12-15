import streamlit as st
from rembg import remove, new_session
from PIL import Image
from io import BytesIO
import zipfile

# ================= 页面设置 =================
st.set_page_config(
    page_title="高级批量抠图工具",
    page_icon="🖼️",
    layout="centered"
)

st.title("🖼️ 在线高级批量抠图工具")
st.caption("支持多模型选择 + 批量上传，AI 智能移除背景")

# ================= 模型选择 =================
model_options = {
    "isnet-general-use": "🌟 推荐：产品/物体（边缘最自然）",
    "u2net": "📦 默认通用模型",
    "u2netp": "⚡ 轻量快速（适合小图）",
    "u2net_human_seg": "👤 人物专用（头发丝超准）",
    "isnet-anime": "🎨 动漫/插画风格"
}

selected_model = st.selectbox(
    "选择 AI 模型",
    options=list(model_options.keys()),
    format_func=lambda x: model_options[x],
    index=0  # 默认选推荐模型
)

# ================= 上传图片 =================
uploaded_files = st.file_uploader(
    "上传图片（支持批量 JPG/PNG/WEBP）",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True,
    help="一次可上传多张，处理后打包下载透明 PNG"
)

if uploaded_files:
    if st.button("🚀 开始批量抠图", type="primary", use_container_width=True):
        # 加载选择的模型（首次会下载，对应模型大小 100-300MB）
        with st.spinner(f"加载 {model_options[selected_model]} 模型（首次稍慢）..."):
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
                    output_image = remove(input_image, session=session)
                    
                    img_byte_arr = BytesIO()
                    output_image.save(img_byte_arr, format="PNG")
                    zip_file.writestr(
                        uploaded_file.name.rsplit(".", 1)[0] + ".png",
                        img_byte_arr.getvalue()
                    )
                except Exception as e:
                    st.error(f"{uploaded_file.name} 处理失败：{e}")
        
        progress_bar.empty()
        status_text.empty()
        
        st.success(f"🎉 完成！使用 **{model_options[selected_model]}** 成功处理 {len(uploaded_files)} 张")
        output_zip.seek(0)
        
        st.download_button(
            label="📦 下载全部透明图（ZIP 包）",
            data=output_zip,
            file_name=f"抠图结果_{selected_model}.zip",
            mime="application/zip",
            use_container_width=True
        )
else:
    st.info("👆 请上传图片并选择模型开始抠图～")

st.markdown("---")
st.caption("基于 rembg 多模型 · 完全免费 · 图片即时处理不保存")
