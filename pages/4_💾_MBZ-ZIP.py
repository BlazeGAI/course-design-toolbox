import streamlit as st
import zipfile
import os
from pathlib import Path

# Function to extract .mbz and re-zip as .zip
def mbz_to_zip(mbz_file_path):
    # Extracting the .mbz (which is essentially a zip file)
    with zipfile.ZipFile(mbz_file_path, 'r') as zip_ref:
        extract_dir = mbz_file_path.stem  # Directory named after the .mbz file
        zip_ref.extractall(extract_dir)

    # Zipping the extracted content into a new .zip file
    zip_file_path = mbz_file_path.with_suffix('.zip')
    with zipfile.ZipFile(zip_file_path, 'w') as zip_ref:
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                full_path = os.path.join(root, file)
                zip_ref.write(full_path, os.path.relpath(full_path, extract_dir))

    # Cleanup extracted directory after re-zipping
    for root, dirs, files in os.walk(extract_dir, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
    os.rmdir(extract_dir)

    return zip_file_path

# Streamlit interface
st.title("MBZ to ZIP Converter")

uploaded_file = st.file_uploader("Upload an .mbz file", type=["mbz"])

if uploaded_file:
    # Save the uploaded file temporarily
    temp_file_path = Path(f"/tmp/{uploaded_file.name}")
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.write("Processing the file...")

    # Convert the MBZ file to ZIP
    zip_file_path = mbz_to_zip(temp_file_path)

    # Provide a download link for the new ZIP file
    with open(zip_file_path, "rb") as f:
        st.download_button(
            label="Download ZIP",
            data=f,
            file_name=zip_file_path.name,
            mime="application/zip"
        )

