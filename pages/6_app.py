import streamlit as st
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

def parse_moodle_backup(xml_file):
    """
    Parses a Moodle backup XML file and returns a structured representation of the course.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Get course information
    course_info = root.find("information")
    course_name = course_info.find("original_course_fullname").text if course_info is not None else "Unknown Course"

    # Extract sections and content
    sections = root.findall("activities/activity")
    course_structure = []

    for section in sections:
        section_name = section.find("title").text if section.find("title") is not None else "Unnamed Section"

        # Extract resources within the section
        resources = section.findall("subplugin")
        resources_list = []

        for res in resources:
            resource_name = res.find("name").text if res.find("name") is not None else "Unnamed Resource"
            resources_list.append(resource_name)

        course_structure.append({"section": section_name, "resources": resources_list})

    return course_name, course_structure

def scrape_live_content(session, url):
    """
    Scrapes content from the Moodle course's live site.

    Args:
    - session: requests.Session() object for authenticated requests.
    - url: URL of the course section or activity to scrape.
    """
    response = session.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract and return relevant content as needed, e.g., text or activity content
    return soup.get_text()

def main():
    st.title("Moodle Backup to Text Converter")

    uploaded_file = st.file_uploader("Choose an XML file", type=["xml"])

    # Collect credentials
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if uploaded_file is not None and username and password:
        # Parse the uploaded XML file
        course_name, course_structure = parse_moodle_backup(uploaded_file)

        st.write(f"Course Name: {course_name}")

        content_output = [f"Course: {course_name}\n"]

        # Setup session
        session = requests.Session()

        # Login to Moodle platform
        login_url = "https://moodle.example.com/login/index.php"  # Adjust this to your Moodle login URL
        session.post(login_url, data={"username": username, "password": password})

        for sec in course_structure:
            section_name = sec['section']
            st.write(f"Section: {section_name}")
            content_output.append(f"Section: {section_name}")

            for res in sec['resources']:
                st.write(f"  - Resource: {res}")
                content_output.append(f"  - Resource: {res}")

                # Fetch and append live content (adjust URL construction accordingly)
                resource_url = f"https://moodle.example.com/course/resource/{res}"  # Adjust this for your Moodle structure
                live_content = scrape_live_content(session, resource_url)
                content_output.append(live_content)

            content_output.append("\n")

        # Save content to a text file
        text_file_content = "\n".join(content_output)
        st.download_button(label="Download as Text File",
                           data=text_file_content,
                           file_name=f"{course_name}_structure.txt",
                           mime="text/plain")

if __name__ == "__main__":
    main()
