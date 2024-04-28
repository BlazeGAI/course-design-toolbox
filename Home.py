import streamlit as st

st.set_page_config(
    page_title="TU COEL Build Toolbox",
    page_icon="👋",
)

st.write("# Welcome to the Tiffin University COEL Course Build Toolbox! 👋")

st.markdown(
    """
These applications serve as an all-in-one tool designed to assist in the course building process, specifically tailored for enhancing the efficiency and effectiveness of preparing online course materials. Here's how it can be beneficial:

### Streamlining the Course Build Process
1. **HTML Formatting for Course Plan HTML**: 
   - This application automatically checks and modifies the headings in your Course Build Plan HTML to adhere to the standard Course Build Plan template.
   - It provides functionality to format this HTML content according to a standard or custom template, ensuring coding accuracy during the merge process.

2. **Moodle HTML Merge**:
   - This tool's ability to merge your Course Build Plan with the Moodle HTML Template streamlines the integration process. It guarantees the accurate representation of your formatted HTML, eliminating coding errors and the need for extensive manual edits.   
   - Utilizing this application can significantly reduce time spent in the course building stage.

3. **Image Resizing**:
   - Facilitating the process of image inclusion, the application offers a feature to resize multiple images simultaneously.
   - Instead of editing each image individually, you can now resize all images in a single folder in one go, enhancing efficiency and saving time.

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
st.sidebar.title("COEL Course Build Toolbox")
st.sidebar.success("Select an application above.")
st.sidebar.image("https://i.imgur.com/PD23Zwd.png", width=250)
    
