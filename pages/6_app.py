import xml.etree.ElementTree as ET
import streamlit as st

def parse_moodle_backup(xml_file):
    """
    Parses a Moodle backup XML file and returns a structured representation of the course.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Information about the course
    course_info = root.find("information")
    course_name = course_info.find("original_course_fullname").text if course_info is not none else "Unknown Course"

    # Sections and content
    sections = root.findall("activities/activity")
    course_structure = []

    for section in sections:
        section_name = section.find("title").text if section.find("title") is not None else "Unnamed Section"

        # Extract resources
        resources = section.findall("subplugin")
        resources_list = []

        for res in resources:
            resource_name = res.find("name").text if res.find("name") is not None else "Unnamed Resource"
            resources_list.append(resource_name)

        course_structure.append({"section": section_name, "resources": resources_list})

    return course_name, course_structure

def main():
    # Streamlit UI
    st.title("Moodle Backup to Text Converter")
    st.write("Upload a Moodle backup XML file to extract and save its content as a text file.")

    uploaded_file = st.file_uploader("Choose an XML file", type=["xml"])

    if uploaded_file is not none:
        # Parse the uploaded XML file
        course_name, course_structure = parse_moodle_backup(uploaded_file)

        # Display the course content on the Streamlit app
        st.write(f"Course Name: {course_name}")

        content_output = [f"Course: {course_name}\n"]

        for sec in course_structure:
            st.write(f"Section: {sec['section']}")
            content_output.append(f"Section: {sec['section']}")
            for res in sec['resources']:
                st.write(f"  - Resource: {res}")
                content_output.append(f"  - Resource: {res}")

            content_output.append("\n")

        # Save content as a text file
        text_file_content = "\n".join(content_output)
        st.download_button(label="Download as Text File",
                           data=text_file_content,
                           file_name=f"{course_name}_structure.txt",
                           mime="text/plain")

if __name__ == "__main__":
    main()

