import streamlit as st
from rembg import remove, new_session
from PIL import Image
from io import BytesIO
import zipfile

st.set_page_config(page_title="专业抠图工具", page_icon="🖼️", layout="centered")

st.title("🖼️ 专业在线抠图工具")
st.caption("支持单张实时预览 + 批量处理 + 多模型 + 边缘优化")

# ================= 模型选择 =================
model_options = {
    "isnet-general-use": "🌟 推荐：产品/物体（边缘最自然）",
    "u2net": "📦 默认通用",
    "u2netp": "⚡ 轻量快速",
    "u2net_human_seg": "👤 人物专用",
    "isnet-anime": "🎨 动漫风格"
}

selected_model = st.selectbox(
    "选择 AI 模型",
    options=list(model_options.keys()),
    format_func=lambda x: model_options[x],
    index=0
)

# ================= 高级设置 =================
with st.expander("🔧 高级优化设置"):
    alpha_matting = st.checkbox("开启 Alpha Matting（精细边缘，推荐开启）", value=True)
    if alpha_matting:
        erode_size = st.slider("边缘腐蚀大小（去黑边）", 5, 25, 15)
        fg_threshold = st.slider("前景阈值", 200, 255, 240)
        bg_threshold = st.slider("背景阈值", 0, 50, 10)
    
    white_bg_option = st.checkbox("生成白底版（电商专用）", value=True)

# ================= 上传图片 =================
uploaded_files = st.file_uploader(
    "上传图片（单张实时预览 / 多张批量处理）",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True,
    help="单张：立即预览结果 | 多张：处理后打包下载"
)

if uploaded_files:
    # 加载模型
    with st.spinner(f"加载 {model_options[selected_model]} 模型..."):
        session = new_session(selected_model)

    # 单张模式：实时预览
    if len(uploaded_files) == 1:
        uploaded_file = uploaded_files[0]
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("原图")
            st.image(uploaded_file, use_column_width=True)
        
        with col2:
            st.subheader("抠图结果（透明背景）")
            with st.spinner("抠图中..."):
                input_image = Image.open(uploaded_file).convert("RGBA")
                output_image = remove(
                    input_image,
                    session=session,
                    alpha_matting=alpha_matting,
                    alpha_matting_foreground_threshold=fg_threshold if alpha_matting else 240,
                    alpha_matting_background_threshold=bg_threshold if alpha_matting else 10,
                    alpha_matting_erode_size=erode_size if alpha_matting else 10
                )
                st.image(output_image, use_column_width=True)
                
                # 白底预览
                if white_bg_option:
                    st.subheader("白底效果预览")
                    white_bg_img = Image.new("RGB", output_image.size, (255, 255, 255))
                    white_bg_img.paste(output_image, mask=output_image.split()[-1])
                    st.image(white_bg_img, use_column_width=True)
        
        # 下载按钮
        buf = BytesIO()
        output_image.save(buf, format="PNG")
        st.download_button("下载透明图", buf.getvalue(), uploaded_file.name.rsplit(".", 1)[0] + ".png", "image/png")
        
        if white_bg_option:
            white_buf = BytesIO()
            white_bg_img.save(white_buf, format="JPEG", quality=95)
            st.download_button("下载白底图", white_buf.getvalue(), uploaded_file.name.rsplit(".", 1)[0] + "_white.jpg", "image/jpeg")
    
    # 批量模式：进度条 + 打包下载
    else:
        if st.button("🚀 开始批量抠图", type="primary", use_container_width=True):
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
                        output_image = remove(
                            input_image,
                            session=session,
                            alpha_matting=alpha_matting,
                            alpha_matting_foreground_threshold=fg_threshold if alpha_matting else 240,
                            alpha_matting_background_threshold=bg_threshold if alpha_matting else 10,
                            alpha_matting_erode_size=erode_size if alpha_matting else 10
                        )
                        
                        # 透明版
                        trans_io = BytesIO()
                        output_image.save(trans_io, format="PNG")
                        zip_file.writestr(uploaded_file.name.rsplit(".", 1)[0] + "_透明.png", trans_io.getvalue())
                        
                        # 白底版
                        if white_bg_option:
                            white_img = Image.new("RGB", output_image.size, (255, 255, 255))
                            white_img.paste(output_image, mask=output_image.split()[-1])
                            white_io = BytesIO()
                            white_img.save(white_io, format="JPEG", quality=95)
                            zip_file.writestr(uploaded_file.name.rsplit(".", 1)[0] + "_白底.jpg", white_io.getvalue())
                    
                    except Exception as e:
                        st.error(f"{uploaded_file.name} 处理失败：{e}")
            
            progress_bar.empty()
            status_text.empty()
            st.success(f"🎉 批量完成！处理 {len(uploaded_files)} 张")
            output_zip.seek(0)
            st.download_button(
                "📦 下载全部结果（ZIP）",
                output_zip,
                "批量抠图结果.zip",
                "application/zip",
                use_container_width=True
            )

else:
    st.info("👆 请上传图片开始抠图（单张实时预览 / 多张批量处理）")

st.markdown("---")
st.caption("多模型 + Alpha Matting 优化 · 支持单张预览 · 完全免费")
