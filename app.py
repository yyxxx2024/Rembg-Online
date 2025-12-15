import streamlit as st
from rembg import remove, new_session
from PIL import Image
from io import BytesIO
import zipfile

# ================= 页面设置 =================
st.set_page_config(
    page_title="批量产品抠图工具",
    page_icon="🖼️",
    layout="centered"
)

st.title("🖼️ 在线批量产品抠图工具")
st.caption("支持批量上传图片，AI 自动移除背景（使用 isnet-general-use 模型，产品图效果最佳）")

# ================= 上传图片 =================
uploaded_files = st.file_uploader(
    "上传产品图片（支持 JPG / PNG / WEBP，批量上传）",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True,
    help="一次可上传多张，处理完成后打包下载透明 PNG"
)

if uploaded_files:
    if st.button("🚀 开始批量抠图", type="primary", use_container_width=True):
        # 创建 isnet-general-use 模型会话（第一次访问会自动下载模型，稍慢）
        with st.spinner("加载 AI 模型（首次稍慢）..."):
            session = new_session("isnet-general-use")

        progress_bar = st.progress(0)
        status_text = st.empty()
        
        output_zip = BytesIO()
        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for idx, uploaded_file in enumerate(uploaded_files):
                # 更新进度条
                progress = (idx + 1) / len(uploaded_files)
                progress_bar.progress(progress)
                status_text.text(f"处理中：{uploaded_file.name} ({idx + 1}/{len(uploaded_files)})")
                
                try:
                    # 读取并处理图片
                    input_image = Image.open(uploaded_file).convert("RGBA")
                    output_image = remove(input_image, session=session)
                    
                    # 保存到 ZIP
                    img_byte_arr = BytesIO()
                    output_image.save(img_byte_arr, format="PNG")
                    zip_file.writestr(
                        uploaded_file.name.rsplit(".", 1)[0] + ".png",
                        img_byte_arr.getvalue()
                    )
                except Exception as e:
                    st.error(f"处理 {uploaded_file.name} 时出错：{e}")
        
        # 完成
        progress_bar.empty()
        status_text.empty()
        
        st.success(f"🎉 完成！成功处理 {len(uploaded_files)} 张图片")
        output_zip.seek(0)
        
        st.download_button(
            label="📦 下载全部透明图（ZIP 包）",
            data=output_zip,
            file_name="产品抠图结果.zip",
            mime="application/zip",
            use_container_width=True
        )
else:
    st.info("👆 请上传图片开始批量抠图～")

st.markdown("---")
st.caption("基于 rembg + isnet-general-use 模型 · 完全免费 · 图片仅用于即时处理，不保存")
