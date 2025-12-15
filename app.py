import streamlit as st
from rembg import remove
from PIL import Image
from io import BytesIO
import zipfile
import time

st.set_page_config(page_title="批量产品抠图工具", page_icon="🖼️", layout="centered")

st.title("🖼️ 在线批量产品抠图工具")
st.caption("支持同时上传多张图片，AI 自动移除背景，输出透明 PNG")

uploaded_files = st.file_uploader(
    "上传产品图片（支持 JPG/PNG，批量上传）",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("🚀 开始批量抠图", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        output_zip = BytesIO()
        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for idx, uploaded_file in enumerate(uploaded_files):
                # 更新进度
                progress = (idx + 1) / len(uploaded_files)
                progress_bar.progress(progress)
                status_text.text(f"处理中：{uploaded_file.name} ({idx+1}/{len(uploaded_files)})")
                
                # 处理图片
                input_image = Image.open(uploaded_file).convert("RGBA")
                output_image = remove(input_image)
                
                # 保存到 ZIP
                img_byte_arr = BytesIO()
                output_image.save(img_byte_arr, format="PNG")
                zip_file.writestr(uploaded_file.name.rsplit(".", 1)[0] + ".png", img_byte_arr.getvalue())
        
        output_zip.seek(0)
        progress_bar.empty()
        status_text.empty()
        
        st.success(f"🎉 完成！成功处理 {len(uploaded_files)} 张图片")
        st.download_button(
            label="📥 下载全部透明图 (ZIP 包)",
            data=output_zip,
            file_name="抠图结果.zip",
            mime="application/zip"
        )
else:
    st.info("👆 请上传图片开始抠图～支持批量上传，处理后打包下载")

st.markdown("---")
st.caption("基于 rembg AI 模型 · 完全免费 · 隐私保护（图片不保存）")
