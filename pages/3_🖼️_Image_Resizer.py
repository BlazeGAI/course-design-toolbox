import os
import streamlit as st
from PIL import Image
from pathlib import Path
import tempfile
import shutil
import base64

st.set_page_config(
page_title="Image Resizer",
page_icon="🖼️",)
st.title("Image Resizer")
st.sidebar.header("Image Resizer")
st.sidebar.write(
    """This application allows users to resize images. You can upload multiple images, choose one of the common image sizes we use, and download the resized images as a single zip file."""
    )
st.sidebar.image("https://i.imgur.com/PD23Zwd.png", width=250)

def resize_image(input_path, output_path, base_width):
    img = Image.open(input_path)
    w_percent = (base_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((base_width, h_size), Image.Resampling.LANCZOS)
    img.save(output_path)

def save_to_zip(output_folder, zip_path):
    shutil.make_archive(zip_path, 'zip', output_folder)

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href

def main():

    uploaded_files = st.file_uploader("Choose images to resize", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
    if uploaded_files:
        resize_option = st.selectbox('Choose the new width for the images:', [400, 800, 1900])

        if st.button('Resize Images'):
            with tempfile.TemporaryDirectory() as temp_dir:
                output_folder = Path(temp_dir) / 'Resized'
                output_folder.mkdir(parents=True, exist_ok=True)

                for uploaded_file in uploaded_files:
                    file_path = Path(temp_dir) / uploaded_file.name
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    with Image.open(file_path) as img:
                        if img.width < 800 and resize_option == 800:
                            if not st.checkbox(f'Enlarge {file_path.name}?', key=file_path):
                                continue

                    new_file_name = f"{file_path.stem}-{resize_option}{file_path.suffix}"
                    output_file = output_folder / new_file_name
                    resize_image(file_path, output_file, resize_option)

                zip_path = Path(temp_dir) / 'resized_images'
                save_to_zip(output_folder, zip_path)

                zip_file = f"{zip_path}.zip"
                if os.path.exists(zip_file):
                    st.markdown(get_binary_file_downloader_html(zip_file, 'Resized Images'), unsafe_allow_html=True)
                else:
                    st.error("Error in creating zip file.")

if __name__ == '__main__':
    main()

st.markdown("""

### Using the Application
If you are using Google to store images, you should name your files before you resize them. It will save you from having to rename them again later.
1. **Upload Images:**
   - Look for the 'Choose images to resize' section on the application page.
   - Click on the upload area or drag and drop your images into it.
   - The application supports 'jpg', 'jpeg', and 'png' file formats.

2. **Select Resize Option:**
   - After uploading the images, a dropdown menu titled 'Choose the new width for the images' will appear.
   - Select your desired width from the options provided (e.g., 400, 800, 1900 pixels).

3. **Resize and Download:**
   - Click the 'Resize Images' button to start the resizing process.
   - Once the resizing is complete, a download link for a zip file containing the resized images will appear.
   - Click on the 'Download Resized Images' link to download the zip file to your device.

### Additional Features
- **Enlarge Option:** If any of the images are smaller than the selected resize width, you will be given an option to enlarge them. A checkbox will appear next to each such image. Check the box if you wish to enlarge that image.

### Troubleshooting
- If you encounter any issues or errors, please refresh the page and try again.
- Ensure your images are in the supported formats (jpg, jpeg, png).
""")
