import streamlit as st

st.set_page_config(
    page_title="TU COL Build Toolbox",
    page_icon="👋",
)

st.write("# Welcome to the Tiffin University COL Course Build Toolbox! 👋")

st.markdown(
    """
These applications serve as an all-in-one tool designed to assist in the course building process, specifically tailored for enhancing the efficiency and effectiveness of preparing online course materials. Here's how it can be beneficial:

### Streamlining the Course Build Process

1. **HTML Formatting for Course Plan HTML**  
   - This application automatically checks and modifies headings in your Course Build Plan HTML to match the standard Course Build Plan template.
   - It formats HTML content according to a standard or custom template, ensuring coding accuracy during the merge process.

2. **Moodle HTML Merge**  
   - This tool merges your Course Build Plan with the Moodle HTML Template for accurate integration.
   - It reduces coding errors and limits the need for manual edits, saving time during course building.

3. **Image Resizing**  
   - This application resizes multiple images at once for efficient image inclusion in your course.
   - Resize an entire folder of images in one step instead of processing them individually.

4. **Sections Extractor**  
   - This tool retrieves content from each weekly section in Moodle and compiles it into a downloadable HTML file.
   - It simplifies the process of gathering weekly materials for review or editing.

5. **Activity Extractor**  
   - This application scans the Gradebook Setup for activity links and consolidates each activity’s NextGen4 content into a single HTML file.
   - It provides a convenient way to assemble and review individual activities without manual copying.


### Enhancing Course Design and Delivery
- **Efficiency**: Saves time by automating the formatting and resizing processes, allowing you to focus more on content creation and instructional design.
- **Consistency**: Ensures that all course materials follow a uniform style and format, contributing to a professional look and feel.
- **Compatibility**: By aligning with Moodle’s requirements, it minimizes technical glitches and streamlines the course upload process.

### Practical Applications
- **For New Course Development**: Ideal for creating new courses from scratch, ensuring that all elements are correctly formatted and integrated from the beginning.
- **Updating Existing Courses**: Useful for revising and updating existing courses, especially when adapting to new templates or platform requirements.
- **Collaboration**: Facilitates collaboration among team members by standardizing the format of course materials, making it easier to share and edit collaboratively.

Overall, this application is a valuable tool for TU educators and course designers looking to enhance the quality and efficiency of their online course development process.
"""
)
st.sidebar.title("COL Course Build Toolbox")
st.sidebar.success("Select an application above.")
st.sidebar.image("https://i.imgur.com/PD23Zwd.png", width=250)
    
